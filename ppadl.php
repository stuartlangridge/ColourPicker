<?php

if (!isset($_GET["pkg"]) || !isset($_GET["owner"]) || !isset($_GET["ppa"])) {
    echo "Bad link.";
    die();
}

$PPAOWNER = $_GET["owner"];
$PPANAME = $_GET["ppa"];
$PACKAGENAME = $_GET["pkg"];

if (!preg_match('/^[a-z0-9.,-]+$/', $PACKAGENAME)) {
    echo "Incorrect package name.";
    die();
}
if (!preg_match('/^[a-zA-Z0-9.-]+$/', $PPAOWNER)) {
    echo "Incorrect package owner.";
    die();
}
if (!preg_match('/^[a-zA-Z0-9-]+$/', $PPANAME)) {
    echo "Incorrect PPA name.";
    die();
}

$PACKAGENAME = explode(",", $PACKAGENAME);

$base = "https://code.launchpad.net/~$PPAOWNER/+archive/ubuntu/$PPANAME/+packages";

$f = file_get_contents($base);
preg_match_all('/<a href="([^"]+)_source.changes"/', $f, $m);
if (count($m) == 2) {
    $debs = Array();
    foreach($m[1] as $part) {
        $failed = FALSE;
        foreach($PACKAGENAME as $ppart) {
            if (strpos($part, $ppart) == FALSE) {
                $failed = TRUE;
            }
        }
        if (!$failed) {
            $debs[] = $part . "_all.deb";
        }
    }
    if (count($debs) == 1) {
        header("Location: " . $debs[0]);
    } else if (count($debs) == 0) {
        echo "That download does not seem to be available. Perhaps you can get this app from <a href='$base'>its PPA</a>.";
    } else {
        echo "Sorry, I found more than one possible download. Perhaps you can get this app from <a href='$base'>its PPA</a>.";
        var_dump($debs);
    }
} else {
    echo "Download does not seem to be available. Perhaps you can get this app from <a href='$base'>its PPA</a>.";
}
?>