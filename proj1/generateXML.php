<?php

function generate(){
    global $order;
    $xmlOut = new DOMDocument('1.0', 'utf-8');
    $xmlOut->formatOutput = true;
    $xmlRoot = $xmlOut->createElement("program");
    $xmlRoot->setAttribute("language", "IPPcode20");
    $xmlRoot = $xmlOut->appendChild($xmlRoot);

    while(1) {
        global $fileStream;
        $input = $fileStream;
        $actual = trim(fgets($fileStream));
        $going = parse($actual);

        if($going['value'] == '-99'){
            echo $line;
            break;
        }
        else{
            if(empty($going['fce'])){
            }
            else{
                $xmlInstruction = $xmlOut->createElement("instruction");
                $xmlInstruction->setAttribute("order", $order);
                $xmlInstruction->setAttribute("opcode", $going['fce']);
                if($going['arg1']){
                    $xmlArg1 = $xmlOut->createElement("arg1", $going['arg1'][1]);
                    $xmlArg1->setAttribute("type", $going['arg1'][0]);
                    $xmlInstruction->appendChild($xmlArg1);
                }
                else{

                }
                if($going['arg2']){
                    $xmlArg2 = $xmlOut->createElement("arg2", $going['arg2'][1]);
                    $xmlArg2->setAttribute("type", $going['arg2'][0]);
                    $xmlInstruction->appendChild($xmlArg2);
                }

                if($going['arg3']){
                    $xmlArg3 = $xmlOut->createElement("arg3", $going['arg3'][1]);
                    $xmlArg3->setAttribute("type", $going['arg3'][0]);
                    $xmlInstruction->appendChild($xmlArg3);
                }

              $xmlRoot->appendChild($xmlInstruction);
              }
          }
        }
        
    echo $xmlOut->saveXML();
}
