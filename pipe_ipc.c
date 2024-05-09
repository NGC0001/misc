#include <errno.h>
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/types.h>
#include <unistd.h>

int down[2];
int up[2];
char *const args[] = {NULL};
char *const env[] = {NULL};

int check(int ok, const char *where) {
  if (ok < 0) {
    fprintf(stderr, "%s : %s\n", where, strerror(errno));
    exit(-1);
  }
  return ok;
}

int readline(int fd, char *buf, size_t sz) {
  size_t total = 0;
  while (!total || buf[-1] != '\n') {
    buf[total] = 0;
    ssize_t n = read(fd, buf, sz);
    if (n < 0) {
      if (errno == EINTR) { errno = 0; continue; }
      if (errno == EAGAIN) { errno = 0; continue; }
      check(n, "readline");
    }
    if (n == 0) {
      fprintf(stderr, "eof in readline\n");
      exit(-1);
    }
    buf += n;
    total += n;
    sz -= n;
  }
  return total;
}

int writeall(int fd, char *buf, size_t sz) {
  size_t total = 0;
  while (sz) {
    ssize_t n = write(fd, buf, sz);
    if (n < 0) {
      if (errno == EINTR) { errno = 0; continue; }
      check(n, "writeall");
    }
    if (n == 0) {
      fprintf(stderr, "eof in writeall\n");
      exit(-1);
    }
    buf += n;
    total += n;
    sz -= n;
  }
  return total;
}

void calculate() {
  char buf[1024] = "1+2\n";
  fprintf(stderr, "> %s", buf);
  int sz = strlen(buf);
  writeall(1, buf, sz);
  sz = readline(0, buf, sizeof(buf));
  buf[sz] = 0;
  fprintf(stderr, buf);
  for (int i = 3; i <= 10; ++i) {
    sprintf(buf + sz - 1, "+%d\n", i);
    fprintf(stderr, "> %s", buf);
    sz = strlen(buf);
    writeall(1, buf, sz);
    sz = readline(0, buf, sizeof(buf));
    buf[sz] = 0;
    fprintf(stderr, buf);
  }
}

int main() {
  check(pipe(down), "pipe down");
  check(pipe(up), "pipe up");
  pid_t pid = check(fork(), "fork");
  if (pid == 0) { // child
    check(dup2(down[0], 0), "child down[0]->stdin"); // stdin from down[0]
    check(dup2(up[1], 1), "child up[1]<-stdout"); // stdout to up[1]
    check(close(down[1]), "child close down[1]");
    check(close(up[0]), "child close up[0]");
    check(execve("/usr/bin/bc", args, env), "execve");
  } else { // parent
    check(dup2(down[1], 1), "parent down[1]<-stdout"); // stdout to down[1]
    check(dup2(up[0], 0), "parent up[0]->stdin"); // stdin from up[0]
    check(close(down[0]), "parent close down[0]");
    check(close(up[1]), "parent close up[1]");
    int fflag = check(fcntl(0, F_GETFL), "get file status flag");
    check(fcntl(0, F_SETFL, fflag | O_NONBLOCK), "set file status flag");
    calculate();
  }
  return 0;
}
