#! /usr/bin/awk -f
# Damir Pulatov
# Parse log files generated by Metrix++


BEGIN {
    # print solver's name
    cmd="basename " (ENVIRON["PWD"]);
    cmd | getline solver;
    printf solver;
}
/Average/ {
    if(header == ":: info: Overall metrics for 'std.code.lines:code' metric")
    {
        printf ", " $3;
    }  
    if(header == ":: info: Overall metrics for 'std.general:size' metric")
    {
        printf ", " $3;
    }  
    if(header == ":: info: Overall metrics for 'std.code.complexity:cyclomatic' metric")
    {
        printf ", " $3;
    }  
    if(header == ":: info: Overall metrics for 'std.code.complexity:maxindent' metric")
    {
        printf ", " $3;
    }  
}
/Total/ {
    if(header == ":: info: Overall metrics for 'std.code.lines:code' metric")
    {
        printf ", " $3;
    }  
    if(header == ":: info: Overall metrics for 'std.general:size' metric")
    {
        printf ", " $3;
    }  
    if(header == ":: info: Overall metrics for 'std.code.complexity:cyclomatic' metric")
    {
        printf ", " $3;
    }  
    if(header == ":: info: Overall metrics for 'std.code.complexity:maxindent' metric")
    {
        print ", " $3;
    }  
}
/files in total/ {
    printf ", " $3;
}
/lines:code/ {
    header=$0;
}
/general:size/ {
    header=$0;
}
/complexity:cyclomatic/ {
    header=$0;
}
/complexity:maxindent/ {
    header=$0;
}
