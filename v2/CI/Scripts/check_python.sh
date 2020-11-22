#!/bin/sh
rm -f pylint.xml
rm -f file.txt

if  [ ! -n "$1" ]; then
	echo "The code sub path parameter is null."
	exit 1
fi

codePath=$WORKSPACE/$1
if [ ! -d $codePath ]; then
	echo "No such directory:$codePath"
	exit 1
fi

#找出源码下所有python文件
find $codePath -name *.py -a ! -name __init__.py > file.txt

echo "====check python file list===="
for var in `cat file.txt` 
do
	echo ${var}
done
echo "=============================="

for var in `cat file.txt` 
do
	pylint --rcfile=$WORKSPACE/pylint.conf --output-format=parseable ${var} >>pylint.xml
done
cat pylint.xml
exit 0