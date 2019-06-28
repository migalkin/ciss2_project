#!/bin/bash
max=`ls -1v /data/dchaudhu/KDDS/Query_1st/kdds-amt/data/logs/create_hit_*| tail -1| tr -dc '0-9'|cut -c2-`
#echo $max
next_f=`expr $max + 1`
echo "create_hit_tree"$next_f".log"
echo "Creating HIT trees"
/data/dchaudhu/anaconda3/envs/py2.7/bin/python -u /data/dchaudhu/KDDS/Query_1st/kdds-amt/create_hit_tree.py --conf /data/dchaudhu/KDDS/Query_1st/kdds-amt/resources/prod_hit_tree.yml > /data/dchaudhu/KDDS/Query_1st/kdds-amt/data/logs/"create_hit_tree"$next_f".log"
echo "Finished the script!"
