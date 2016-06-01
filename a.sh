export s=`python -c 'import time; print time.time()'`
screencapture t.jpg
export e=`python -c 'import time; print time.time()'`
echo $e-$s

