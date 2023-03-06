cd input
for dir in `ls -d */ | cut -f1 -d'/'`
do
    echo "$dir start"
    python ../marker.py -f ./$dir -o ../output -l $dir
    echo "$dir end"
done
cd ..
start output