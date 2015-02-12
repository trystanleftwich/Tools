#!/bin/bash
help()  {
    echo "USAGE: network_perf.sh --add|--remove -d=|--device=<string> [-p=|--packetloss=<percent value>] [-l=|--latency=<ms val>] [--random-latency=<ms val>] [-b=--bandwidth=<kbps value>]"
    echo ""
    echo "-a|--add:                                 Add network performance to the device"
    echo "-r|--remove:			            Remove any settings on the device"
    echo "-d=|--device=<string>:                    The name of the network device you want to run on, IE eth0"
    echo "-p=|--packetloss=<percent value>:         The percent of packetloss you want, IE 10%, DEFAULT:2%"
    echo "-l=|--latency=<ms val>:                   The amount of latency you would like IE 100ms, DEFAULT:100ms"
    echo "--random-latency=<ms val>:                Add a random factor to the latency number above IE 10ms will give a latency of between 90 and 110ms, DEFAULT:10ms"
    echo "-b=--bandwidth=<kb value>:                Limit the amount of bandwidth on the device: IE 1000kb will limit it to 1mb, DEFAULT: 1000kbps"
    exit 1
}

remove() {
	echo "Removing all network perf options on device: $DEVICE"
	tc qdisc del dev $DEVICE root
}

if [ "$EUID" -ne 0 ]
  then echo "Please run the script as root user"
  exit
fi


if [[ -z "$@" ]]; then
	help
fi


for i in "$@"; do
    case $i in
	-a|--add)
	ADD="true"
	shift
	;;
        -r|--remove)
	REMOVE="true"
	shift
	;;
        -d=*|--device=*)
        DEVICE="${i#*=}"
        shift
        ;;
        -p=*|--pocketloss=*)
        PACKETLOSS="${i#*=}"
        shift
        ;;
        -l=*|--latency=*)
        LATENCY="${i#*=}"
        shift
        ;;
        --random-latency=*)
        RANDOMLATENCY="${i#*=}"
        shift
        ;;
        -b=*|--bandwidth=*)
        BANDWIDTH="${i#*=}"
        shift
        ;;
        *)
         help
         ;;
    esac
done

if [[ -z "$ADD" && -z "$REMOVE" ]]; then
	echo "Missing add/remove statment"
	help
fi

if [[ -z "$DEVICE" ]]; then
	echo "You need to set a device"
	help
fi

if [[ -z "$PACKETLOSS" ]]; then
	PACKETLOSS="2%"
fi

if [[ -z "$LATENCY" ]];then
	LATENCY="100ms"
fi

if [[ -z "$BANDWIDTH" ]];then
	BANDWIDTH="1000kbps"
fi

if [[ -z "$RANDOMLATENCY" ]]; then
	RANDOMLATENCY="10ms"
fi


if [[ -n "$ADD" ]]; then
   if [ `tc qdisc show | grep eth1 | grep -c parent` -gt 0 ]; then
   	echo "You already have network options on device: $DEVICE"
   	remove
   fi
   echo "Adding latency: $LATENCY with random_latency: $RANDOMLATENCY and packetloss: $PACKETLOSS with bandwidth: $BANDWIDTH, to device: $DEVICE"
   tc qdisc add dev $DEVICE root handle 1: htb default 12 
   tc class add dev $DEVICE parent 1:1 classid 1:12 htb rate $BANDWIDTH ceil $BANDWIDTH
   tc qdisc add dev $DEVICE parent 1:12 netem delay $LATENCY $RANDOMLATENCY loss $PACKETLOSS
fi

if [[ -n "$REMOVE" ]]; then
	remove
fi

