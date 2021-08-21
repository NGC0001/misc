// https://unix.stackexchange.com/questions/130906/why-does-setuid-not-work

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/types.h>
#include <unistd.h>

#define MaxStrLen 1024

int main(int argc, char* argv[]) {
    char cmd[MaxStrLen+1] = {0};
    int i = 0;
    int len = 0, idx = 0;
    setuid(0);
    if (argc >= 2) {
        for (idx = 0, i = 1; i < argc; ++i) {
            len = strlen(argv[i]) + 1;
            if (idx + len > MaxStrLen) {
                fprintf(stderr, "Error: Arguments too long.\n");
                return -1;
            }
            strcpy(cmd+idx, argv[i]);
            cmd[idx + len - 1] = ' ';
            idx += len;
        }
        cmd[idx] = 0;
        // printf("cmd[%ld]: %s\n", strlen(cmd), cmd);
        return system(cmd);
    }
    return system("/bin/bash");
}