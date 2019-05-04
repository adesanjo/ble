fun prime(n)->{
    p = true;
    for j = 3 to n step 2 then{
        if i % j == 0 then{
            p = false;
        };
    };
    p;
};

limit = input + 1;

if limit > 2 then{
    disp 2;
};
for i = 3 to limit step 2 then{
    if prime(i) then{
        disp i;
    };
};