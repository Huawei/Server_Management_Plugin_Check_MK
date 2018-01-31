#!/bin/sh

SRCDIR=$(cd `dirname $0`; pwd)
cmkdir="$(echo "$SRCDIR" | sed -rn "s/(.+)\/build/\1/gp")"
#datetime=$(date "+%Y-%m-%d-%H-%M-%S")
#echo $datetime
rm -rf $cmkdir/releases/* && mkdir -p $cmkdir/releases/cmkplugin_latest &&
cd $cmkdir/src/modules && tar zcf modulesplugin.tar.gz *.py  huawei_server && mv modulesplugin.tar.gz $cmkdir/releases/cmkplugin_latest/ &&
chmod a+x $SRCDIR/{setup.sh,uninstall.sh} &&
cp $SRCDIR/{setup.sh,uninstall.sh} $cmkdir/releases/cmkplugin_latest/ &&
cd $cmkdir/releases &&
tar zcf cmkplugin_latest.tar.gz cmkplugin_latest &&
rm -rf $cmkdir/releases/cmkplugin_latest
