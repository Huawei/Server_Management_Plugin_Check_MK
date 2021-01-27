#!/bin/sh

SRCDIR=$(cd `dirname $0`; pwd)
cmkdir="$(echo "$SRCDIR" | sed -rn "s/(.+)\/build/\1/gp")"
#datetime=$(date "+%Y-%m-%d-%H-%M-%S")
#echo $datetime
#tarname=cmkplugin_$1
tarname=$1
rm -rf $cmkdir/releases/* && mkdir -p $cmkdir/releases/$tarname &&
cd $cmkdir/src/modules && tar zcf modulesplugin.tar.gz *.py  huawei_server && mv modulesplugin.tar.gz $cmkdir/releases/$tarname/ &&
chmod a+x $SRCDIR/{setup.sh,uninstall.sh} &&
cp $SRCDIR/{setup.sh,uninstall.sh,setup.py} $cmkdir/releases/$tarname/ &&
cp -rf $SRCDIR/../lib/*  $cmkdir/releases/$tarname/ &&
cd $cmkdir/releases &&
tar zcvf $tarname.tar $tarname &&
rm -rf $cmkdir/releases/$tarname
