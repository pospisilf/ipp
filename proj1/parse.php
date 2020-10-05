<?php
#IPPcode20 - IPP projekt č. 1
#Autor - Filip Pospíšil
#xpospi0f@stud.fit.vutbr.cz

#připojené soubory
require_once("./generateXML.php");
require_once("./scanner.php");

#konstanty
const wrongParameter = 10;
const inputFileErr = 11;
const outputFileErr = 12;
const headerErr = 21;
const wrongCode = 22;
const lexicalError = 23;
const internalRunErr = 99;

global $order;

//parsování argumentů
$sOptions = "h";
$lOptions = array("help");
if(array_key_exists("help", getopt($sOptions, $lOptions)) || array_key_exists("h", getopt($sOptions, $lOptions))){
    if ($argv[1] == "--help" || $argv[1] == "-h" && $argc == 2) {
        echo "IPPcode20 parse.php \n";
        echo "-h nebo --help pro napovedu\n";
        echo "Vytvari XML ze STDINu.\n";
        exit(0);
    }
    else {
        exit(wrongParameter);
    }
}

#kontorla hlavickyy
$fileStream = fopen( 'php://stdin', 'r' );
$actual = strtolower(fgets($fileStream));
if(!preg_match("^.ippcode20^", $actual)){
    fwrite(STDERR, "Syntax error: Chybejici hlavicka!\n");
    exit(headerErr);
}

generate();

?>
