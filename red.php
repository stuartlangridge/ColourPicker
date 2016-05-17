<?php
$f = file_get_contents("https://code.launchpad.net/~sil/+archive/ubuntu/pick/+packages");
preg_match('/<a href="([^"]+)_source.changes"/', $f, $m);
if (count($m) == 2) {
    $nurl = $m[1] . "_all.deb";
    echo $nurl;
} else {
    echo 'Download does not seem to be available. Perhaps you can get Pick from <a href="https://code.launchpad.net/~sil/+archive/ubuntu/pick/">the Pick PPA</a>.';
}
?>