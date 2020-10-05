<?php
#IPPcode20 - IPP projekt č. 3
#Autor - Filip Pospíšil
#xpospi0f@stud.fit.vutbr.cz

#debug variable
$debug = 0;

#Výchozí proměnné
$directory = "./";
$scriptParse = "./parse.php";
$scriptParseChange = false;
$scriptInterpret = "./interpret.py";
$scriptInterpretChange = false;
$recursiveFlag = false;
$parseOnly = false;
$interpretOnly = false;
$jexamxml = "/pub/courses/ipp/jexamxml/jexamxml.jar";
$timestart = microtime(true);
$parseOutput = tempnam("/tmp", "");
$intOutput = tempnam("/tmp", "");
$infile;
$outfile;
$rcFile;
$test_counter = 0;
$test_passed = 0;


# <--- PARSOVANI ARGUMENTU --->
$sOptions = "";
$lOptions = array("help", "directory:", "recursive", "parse-script:", "int-script:", "parse-only", "int-only", "jexamxml:");

$options = getopt($sOptions, $lOptions);


#JE v argumentech napoveda?
if(array_key_exists("help", $options)) {
    #Napovedu nelze kombinvoat s dalsim parametrem!
    if($argc != 2) {
        fwrite(STDERR, "Chybny pocet parametru.\n");
        exit(10);
    }
    napoveda();
}

if(array_key_exists("directory", $options)) {
    $directory = $options["directory"];
}

if(array_key_exists("recursive", $options)) {
    $recursiveFlag = true;
}

if(array_key_exists("parse-script", $options)) {
    $scriptParse = $options["parse-script"];
    $scriptParseChange = true;
}

if(array_key_exists("int-script", $options)) {
    $scriptInterpret = $options["int-script"];
    $scriptInterpretChange = true;
}

if(array_key_exists("parse-only", $options)) {
    $parseOnly = true;
}

if(array_key_exists("int-only", $options)) {
    $interpretOnly = true;
}

if(array_key_exists("jexamxml", $options)) {
    $jexamxml = $options["jexamxml"];
}

if($parseOnly && $interpretOnly) {
    exit(10);
}

if($parseOnly && $scriptInterpretChange) {
    exit(10);
}

if($interpretOnly && $scriptParseChange) {
    exit(10);
}


if(!file_exists($directory)) {
    fwrite(STDERR, "Error: directory neexistuje.\n");
    exit(11);
}

if(!file_exists($scriptParse)) {
    if($interpretOnly){
        pass;
    }
    else{
        fwrite(STDERR, "Error: Parser file neexistuje.\n");
        exit(11);
    }
}

if(!file_exists($scriptInterpret)) {
    if($parseOnly){
        pass;
    }
    else{
        fwrite(STDERR, "Error: Interpret file neexistuje.\n");
        exit(11);
    }
}

if(!file_exists($jexamxml)) {
    fwrite(STDERR, "Error: Jexamxml file neexistuje.\n");
    exit(11);
}

# <--- //PARSOVANI ARGUMENTU --->

# <--- Nápověda -->
function napoveda()
{
    echo "IPP2019/2020 projekt č. 3 - test.php\n";
    echo "Dostupné příkazy: \n";
    echo "--help - vypíše tuhle nápovědu\n";
    echo "--directory=path - bude hledat testy v adresáři \"path\" \n";
    echo "--recursive - testy bude hledat i rekurzivně v podadresářích\n";
    echo "--parse-script=file - soubor se skriptem pro analýzu, výchozí parse.php \n";
    echo "--int-script=file - soubor se skriptem pro interpretaci, výchozí interpret.py \n";
    echo "--parse-only - otestuje pouze analýzu\n";
    echo "--int-only - otestuje pouze interpretaci\n";
    echo "--jexaxml=file - soubor s balíčkem pro nástroj JExamXML, výchozí /pub/coueses/ipp/jexamxml/jexamlxml.jar \n";
    exit(0);
}

# <--- //Nápověda --->


scan_directory($directory, $recursiveFlag);

# <--- Prohledávání složek --->
function scan_directory($directory_input, $recursiveFlag)
{
    global $debug;
    global $parseOutput;
    global $intOutput;
    global $parseOnly;
    global $interpretOnly;
    global $infile;
    global $outfile;
    global $rcFile;
    global $test_counter;
    global $test_passed;
    global $jexamxml;

    if($recursiveFlag == true) {
        if($debug == 1) {
            echo "Debug: RECURSIVEFLAG je true, progledavam rekursivne!\n";
        }
        exec("find " . $directory_input . " -regex '.*\.src$'", $test_directory);

    } else {
        exec("find " . $directory_input . " -maxdepth 1 -regex '.*\.src$'", $test_directory);
    }

    build_html_start();

    foreach ($test_directory as $test_dir) {
        $path = explode('/', $test_dir);
        $testName = explode('.', end($path))[0];
        $testPath = "";

        foreach (array_slice($path, 0, -1) as $dir) {
            $testPath = $testPath . $dir . '/';
        }


        $infile = $testPath . $testName . ".in";
        if(!file_exists($infile)) {
            $editfile = fopen($infile, "w");

            if($debug == 1) {
                echo "debug: vytvarim in \n";
            }

            fclose($editfile);
        }

        $outfile = $testPath . $testName . ".out";
        if(!file_exists($outfile)) {
            $editfile = fopen($outfile, "w");

            if($debug == 1) {
                echo "debug: vytvarim out \n";
            }

            fclose($editfile);
        }

        $rcFile = $testPath . $testName . ".rc";
        if(!file_exists($rcFile)) {
            $rc = 0;

            if($debug == 1) {
                echo "debug: vytvarim rc\n";
            }

            $file = fopen($rcFile, "w");
            fwrite($file, "0"); #vychozi navratovy kod je 0!
            fclose($file);
        } else {
            $file = fopen($rcFile, "r");
            $rc = intval(fread($file, filesize($rcFile)));
            fclose($file);
        }

        if($interpretOnly == true) {
            $test_counter++;
            run_interpret_only($test_dir);

        } elseif($parseOnly == true) {
            $test_counter++;
            $parseReturn = run_parse($test_dir);

            $expected_return_value_check = fopen($rcFile, "r");
            $expected_return_value = fopen($rcFile, "r");
            $expected_return_value_check = fopen($rcFile, "r");

            if(fgets($expected_return_value_check) == $parseReturn) {
                if(shell_exec("java -jar " . $jexamxml . " " . $parseOutput . " " . $outfile) == 0) {
                    $test_passed++;

                    uspesny_test($test_counter, $infile, fgets($expected_return_value), $parseReturn);
                } else {

                    neuspesny_test($test_counter, $infile, fgets($expected_return_value), $parseReturn);

                }

            } else {
                neuspesny_test($test_counter, $infile, fgets($expected_return_value), $parseReturn);

            }

            fclose($expected_return_value);
            fclose($expected_return_value_check);

        } else {
            if(run_parse($test_dir) == 0) {
                $test_counter++;
                run_interpret();
            }
        }
    }
    build_html_end();
}

# <--- //Prohledávání složek --->

# <--- Parsování argumentů --->
function run_parse($path)
{
    global $scriptParse;
    global $scriptInterpret;
    global $parseOutput;
    global $intOutput;
    global $infile;

    exec("php7.4 " . $scriptParse . " < " . $path . " 2> /dev/null", $parseOut, $parseReturnCode);
    $parseOut = shell_exec("php7.4 " . $scriptParse . " < " . $path . " 2> /dev/null");

    $outputFile = fopen($parseOutput, "w");

    fwrite($outputFile, $parseOut);
    fclose($outputFile);


    return $parseReturnCode;
    // return 1;
}

# <--- //Parsovní argumentů --->


# <--- Interpret --->
function run_interpret()
{
    global $scriptParse;
    global $scriptInterpret;
    global $parseOutput;
    global $intOutput;
    global $infile;
    global $outfile;
    global $test_passed;
    global $test_counter;
    global $rcFile;

    exec("python3.8 " . $scriptInterpret . " --source=" . $parseOutput . " < " . $infile . " 2> /dev/null", $intOut,
        $intReturnCode);

    $intOut = shell_exec("python3.8 " . $scriptInterpret . " --source=" . $parseOutput . " < " . $infile . " 2> /dev/null");

    $outputFile = fopen($intOutput, "w");
    fwrite($outputFile, $intOut);
    fclose($outputFile);

    $expected_return_value = fopen($rcFile, "r");
    $expected_return_value_check = fopen($rcFile, "r");


    // if (!$intReturnCode) {
    if(fgets($expected_return_value_check) == $intReturnCode) {
        $diff = shell_exec("diff " . $outfile . " " . $intOutput);
        uspesny_test($test_counter, $infile, fgets($expected_return_value), $intReturnCode);
        $test_passed++;
    } else {
        neuspesny_test($test_counter, $infile, fgets($expected_return_value), $intReturnCode);

    }

    fclose($expected_return_value_check);
    fclose($expected_return_value);

}

#<--- //Interpret --->


#<--- Spuštění, pokuď chceme jenom interpret --->
function run_interpret_only($vstupniSouborSrc)
{
    global $scriptParse;
    global $scriptInterpret;
    global $parseOutput;
    global $intOutput;
    global $infile;
    global $outfile;
    global $test_passed;
    global $test_counter;
    global $rcFile;
    global $directory;

    #misto parseOutput uz musi pricahzet soubor!


    exec("python3.8 " . $scriptInterpret . " --source=" . $vstupniSouborSrc . " < " . $infile . " 2> /dev/null", $intOut,
        $intReturnCode);

    $intOut = shell_exec("python3.8 " . $scriptInterpret . " --source=" . $parseOutput . " < " . $infile . " 2> /dev/null");

    $outputFile = fopen($intOutput, "w");
    fwrite($outputFile, $intOut);
    fclose($outputFile);

    $expected_return_value = fopen($rcFile, "r");
    $expected_return_value_check = fopen($rcFile, "r");


    // if (!$intReturnCode) {
    if(fgets($expected_return_value_check) == $intReturnCode) {
        $diff = shell_exec("diff " . $outfile . " " . $intOutput);
        uspesny_test($test_counter, $infile, fgets($expected_return_value), $intReturnCode);
        $test_passed++;
    } else {
        neuspesny_test($test_counter, $infile, fgets($expected_return_value), $intReturnCode);
    }

    fclose($expected_return_value_check);
    fclose($expected_return_value);

}

#<--- //Spuštění, pokuď chceme jenom interpret --->


#<--- Generování neúspěšného testu do html --->
function neuspesny_test($count, $name, $expected, $return)
{
    echo "<font size=\"5\" color=\"red\">$count. test_ $name TEST result :  failed</font><br>\n";
    if($return === "124") {
        echo "<font size=\"5\" color=\"white\" style=\"margin-left: 0\">Program got stucked killed the process</font><br>\n";
    }
    echo "<font size=\"5\" color=\"white\" style=\"margin-left: 0\">Expected return value : $expected - returned : $return</font><br>\n";

    echo "<br>";

}

#<--- //Generování neúspěšného testu do html --->

#<--- Generování úspěšného testu do html --->
function uspesny_test($count, $name, $expected, $return)
{
    echo "<font size=\"5\" color=\"#2ECC40\">$count. test: $name TEST result:  passed</font><br>\n";
    if($return === "124") {
        echo "<font size=\"5\" color=\"white\" style=\"margin-left: 0\">Program got stucked killed the process</font><br>\n";
    }
    echo "<font size=\"5\" color=\"white\" style=\"margin-left: 0\">Expected return value : $expected - returned : $return</font><br>\n";
    echo "<br>";
}

#<--- //Generování úspěšného testu do html --->

#<--- Generování začátku html --->
function build_html_start()
{
    global $test_counter;
    global $test_passed;
    global $parseOnly;
    global $interpretOnly;
    echo "<!DOCTYPE HTML>\n";
    echo "<html>\n";
    echo "<head>\n";
    echo "<meta charset=\"utf-8\">\n";
    echo "<meta name=\"viewport\" content=\"width=1920, initial-scale=1.0\">\n";
    echo "<title>IPP 2019/2020 - výsledky testů</title>\n";
    echo "</head>\n";
    echo "<body style=\"background: #465362\">\n";
    echo "<h1 style=\"color: #FFDC00; text-align: center;\"><font face=\"verdana\">IPP PROJEKT 2019/2020 test.php</font></h1>\n";
    if($parseOnly == true) {
        echo "<h3 style=\"color: white; text-align: center\"><font face=\"verdana\">--pasre-only mode</font></h3>\n";
    } elseif($interpretOnly == true) {
        echo "<h3 style=\"color: white; text-align: center\"><font face=\"verdana\">--int-only mode</font></h3>\n";
    } else {
        echo "<h3 style=\"color: white; text-align: center\"><font face=\"verdana\">parse+interpret mode</font></h3>\n";
    }
    echo "<center>";
    echo "<h3 style=\"color: yellow;\"> <font face=\"verdana\"><a href=\"#shrnuti\" style=\"color:yellow;\">Přejít ke shrnutí</font><a/></h3>";

}

#<--- //Generování začátku html --->

#<--- Generování konce html --->
function build_html_end()
{
    global $test_counter;
    global $test_passed;
    global $timestart;

    $timeend = microtime(true);
    echo "<style>";
    echo "table, th, td {";
    echo "border: 1px solid black;";
    echo "}";
    echo "</style>";
    echo "<h1 id=\"shrnuti\" style=\"color: white;text-align: center\">Shrnutí:</h1>";
    echo "<table style=\"width:40%\">";
    echo "<tr>";
    echo "<th style=\"color: #2ECC40;\"><font size=\"5\">Úspěšných testů:</font></th>";
    echo "<th style=\"color: #2ECC40;\"><font size=\"5\">";
    echo $test_passed;
    echo "</font></th>";
    echo "<th style=\"color: #2ECC40;\"><font size=\"5\">";
    if($test_counter == 0){
        echo "0";
    }
    else{
        echo number_format(($test_passed / $test_counter) * 100, 2, '.', '');
    }
    echo "% </font></th>";
    echo "</tr>";
    echo "<tr>";
    echo "<th style=\"color: red;\"><font size=\"5\">Neúspěšých testů:</font></th>";
    echo "<th style=\"color: red;\"><font size=\"5\">";
    echo $test_counter - $test_passed;
    echo "</font></th>";
    echo "<th style=\"color: red;\"><font size=\"5\">";
    if($test_counter == 0){
        echo "0";
    }
    else{
        echo number_format((($test_counter - $test_passed) / $test_counter) * 100, 2, '.', '');
    }
    echo "% </font></th>";
    echo "</tr>";
    echo "<tr>";
    echo "<th style=\"color: white;\"><font size=\"5\">Testů celkem:</font></th>";
    echo "<th style=\"color: white;\"><font size=\"5\">";
    echo $test_counter;
    echo "</font></th>";
    echo "<th style=\"color: white;\"><font size=\"5\">";
    if($test_counter == 0){
        echo "0";
    }
    else{
        echo ($test_counter / $test_counter) * 100;
    }
    echo "% </font></th>";
    echo "</tr>";
    echo "<tr>";
    echo "<th style=\"color: white;\">Celkový čas testu:</th>";
    echo "<th style=\"color: white;\">";
    echo number_format($timeend - $timestart, 2, '.', '') * 1000;
    echo " ms</th>";
    echo "</tr>";
    echo "</table>";
    echo "</center>";
    echo "</body>\n";
    echo "</html>\n";
}

#<--- //Generování konce html --->


# <--- DEBUG INFORMACE --->
if($debug == 1) {
    echo "\n\n\nDEBUG INFORMATIONS\n";
    echo "directory: ";
    echo $directory;
    echo "\nrecursive: ";
    echo $recursive;
    echo "\nparse-script: ";
    echo $scriptParse;
    echo "\nint-script: ";
    echo $scriptInterpret;
    echo "\nparse-only: ";
    echo $parseOnly;
    echo "\nint-only: ";
    echo $interpretOnly;
    echo "\nparse-script change: ";
    echo $scriptParseChange;
    echo "\nint-script change: ";
    echo $scriptInterpretChange;
    echo "\njexamxml: ";
    echo $jexamxml;
    echo "\n";
}

# <--- //DEBUG INFORMACE --->

?>
