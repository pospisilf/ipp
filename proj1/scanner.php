<?php

function xml_conversion($string){ 
    if(preg_match("/(^(LF|GF|TF)@(\S*))/", $string)){
        $output = array("var", $string);
    }
    else {
        if(preg_match("/^string/i", $string)){
            if(preg_match("/</", $string)){
                $string = preg_replace("/</", htmlspecialchars("<"), $string);
            }
            else if(preg_match("/>/", $string)){
                $string = preg_replace("/>/", htmlspecialchars(">"), $string);
            }
            else if(preg_match("/&/", $string)){
                $string = preg_replace("/&/", htmlspecialchars("&"), $string);
            }
        }
        else if(preg_match("/^(bool|nil)/i", $string)){
            $string = strtolower($string);
        }
        $output = preg_split("/@/", $string, 2);
    }
    return $output;
}

function parse($actual){
    global $order;

    $error = -99;

    if($actual == false){
            return array("value" => "-99");
        }
        else{
            $string = preg_split("/[# ]/", $actual);
            if($string[0] == false){
            }
            else if(preg_match("/(not|int2char|stri2int|read|write|concat|strlen|getchar|setchar|type|label|jump|jumpifeq|jumpifneq|exit|dprint|break|move|createframe|pushframe|popframe|defvar|call|return|pushs|pops|add|sub|mul|idiv|lt|gt|eq|and|or|)/i", $actual)){
                $order++;
                if(preg_match("/^(CREATEFRAME|PUSHFRAME|POPFRAME|break)(\s*#(\s*.*))*$/i", $actual)){
                    return array('value' => '0', 'fce' => $string[0]);
                }
                else if(preg_match("/^(move|in2char|not|strlen|type) ((LF|GF|TF)@(\S*)) ((string@[^#\ ]*)|(nil@nil)|(bool@(true|false))|(int@-?\d*)|((LF|GF|TF)@(\S*)))(\s*#(\s*.*))*$/i", $actual)){
                    return array('value' => '0', 'fce' => $string[0], 'arg1' => array("var", $string[1]), 'arg2' => xml_conversion($string[2]));
                }
                else if(preg_match("/^(add|sub|mul|idiv|lt|gt|eq|and|or|str2int|concat|getchar|setchar) ((LF|GF|TF)@(\S*)) ((string@[^#\ ]*)|(nil@nil)|(bool@(true|false))|(int@-?\d*)|((LF|GF|TF)@(\S*))) ((string@[^#\ ]*$)|(nil@nil)|(bool@(true|false))|(int@-?\d*)|((LF|GF|TF)@(\S*)))(\s*#(\s*.*))?$/i", $actual)){
                    return array('value' => '0', 'fce' => $string[0], 'arg1' => array("var", $string[1]), 'arg2' => xml_conversion($string[2]), 'arg3' => xml_conversion($string[3]));
                }
                else if(preg_match("/^(jump|label|call) [^#\ ]+$/i", $actual)){
                    return array('value' => '0', 'fce' => $string[0], 'arg1' => array("label", $string[1]));
                }
                else if(preg_match("/^defvar ((LF|GF|TF)@(\S*))(\s*#(\s*.*))*$/i", $actual)){
                    return array('value' => '0', 'fce' => $string[0], 'arg1' => array("var", $string[1]));
                }
                else if(preg_match("/^(jumpifeq|jumpifneq) ([^#\ ]+) ((string@[^#\ ]*)|(nil@nil)|(bool@(true|false))|(int@-?\d*)|((LF|GF|TF)@(\S*))) ((string@[^#\ ]*$)|(nil@nil)|(bool@(true|false))|(int@-?\d*)|((LF|GF|TF)@(\S*)))(\s*#(\s*.*))*$/i", $actual)) {
                    return array('value' => '0', 'fce' => $string[0], 'arg1' => array("label", $string[1]), 'arg2' => xml_conversion($string[2]), 'arg3' => xml_conversion($string[3]));
                }
                else if(preg_match("/^(exit|dprint|write) ((string@[^#\ ]*)|(nil@nil)|(bool@(true|false))|(int@-?\d*)|((LF|GF|TF)@(\S*)))(\s*#(\s*.*))*$/i", $actual)){
                    return array('value' => '0', 'fce' => $string[0], 'arg1' => xml_conversion($string[1]));
                }
                else if(preg_match("/^(read) ((LF|GF|TF)@(\S*)) (string|int|bool)(\s*#(\s*.*))*$/i", $actual)){
                    return array('value' => '0', 'fce' => $string[0], 'arg1' => array("type", $string[1]));
                }
                else{
                    exit(lexicalError);
                    }
            }

            else{
                exit(wrongCode);
                }

    }
}

?>
