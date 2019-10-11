y=$(date -d '1 day ago' +"%Y")
m=$(date -d '1 day ago' +"%m")
d=$(date -d '1 day ago' +"%d")
#hadoop fs -getmerge /apps/hive/warehouse/user/duobi/duobi_im_all_$y-$m-$d im$m$d
cat im$m$d | grep $'\t0\t' | awk -F'\t' '{print $1}' | sort | uniq | shuf | head -30000 | sort > shuf.tmp
cat ner.txt | awk -F'\t' '{print $1}' | sort > exists.tmp
sort shuf.tmp exists.tmp exists.tmp | uniq -u > diff.tmp
cat diff.tmp | python toiob.py > data/test.txt
#rm *.tmp

#python evaluate.py
#paste results/conlleval10102019_161059.tmp data/test.txt | python iob2table.py
