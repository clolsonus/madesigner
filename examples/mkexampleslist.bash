#!/bin/bash

for f in example*mad
do 
    echo $f $(grep description $f|perl -pe 's{^ *}{};s{<[^<>]+>}{}g'|head -n1)
done \
> list_of_examples.txt

