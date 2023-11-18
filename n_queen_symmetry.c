#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <assert.h>
#include <string.h>
#include <ctype.h>

#define BIGSTR 1024

#define ARGC_QUIET 2
#define ARGC_VERBOSE 3
#define ARG_VERBOSE_IDX 1
#define ARG_VERBOSE "-verbose"
#define N_MIN 1
#define N_MAX 30
#define MAX_SYMMETRY 8
#define ROT_SYMMETRY 4
#define R_CPR 0
#define R_COL 1
#define R_CMR 2
#define R_LMTS 3

#define NUM_DIGITS 10
#define CHAR_A 'a'
#define CHAR_ZERO '0'
#define CHAR_NEWLINE '\n'
#define CHAR_SPACE ' '
#define CHAR_QUEEN_1 'Q'
#define CHAR_QUEEN_2 'N'
#define BOARD_COLORS 2

/* Code copied from Neill */
#define BACKGROUND 10
typedef enum {
  black=30, red, green, yellow, blue, magenta, cyan, white
} neillcol;
void neillfgcol(const neillcol c);
void neillbgcol(const neillcol c);
void neillreset(void);
/* End of code copied from Neill */

/* Code copied from 8q.c/extension.c */
typedef struct {
  bool valid;
  char err[BIGSTR];
  int n;
  bool verbose;
} user_input_t;
/* ---- */
user_input_t get_user_input(int argc, char *argv[]);
bool is_digit_str(const char *s);
void print_solution(int *cols, int n);
void print_solution_graphic(int *cols, int n);
/* End of code copied from 8q.c/extension.c */

typedef struct {
  int n;
  bool verbose_output;
  int num_solutions;
  int num_fundamental;
} nqueen_t;

typedef struct {
  int col_bits[N_MAX];
  int limits[N_MAX][R_LMTS];
  int masks[N_MAX];
} search_t;

typedef struct {
  int num;
  int solutions[MAX_SYMMETRY][N_MAX];
} solution_group_t;

void test(void);
void solve(nqueen_t *nqueen);
void search(nqueen_t *nqueen, search_t *srch, int row);
void symmetry_mask(int *masks, int n, int row, int col);
void rotate(const int *from, int *to, int n);
void mirror(const int *from, int *to, int n);
bool solutions_eq(const int *b1, const int *b2, int n);
void bits2indices(const int *bits, int *indices, int n);
int msb(unsigned u);
void cols2rows(const int *cols, int *rows, int n);
void copy_solution(const int *from, int *to, int n);
void expand(const int *cols, int n, solution_group_t *sg);
bool is_fundamental(int *cols, int n);
bool is_nonsymmetric_c0_fundamental(int *rot_pos);
bool is_nonsymmetric_inner_fundamental(int *rot_pos,
    bool rot4_sym);

int main(int argc, char *argv[]) {
  test();
  user_input_t input = get_user_input(argc, argv);
  if (!input.valid) {
    fprintf(stderr,
        "%s\n\nusage: %s [%s] N\nwhere: %d <= N <= %d\n",
        input.err, argv[0], ARG_VERBOSE, N_MIN, N_MAX);
    exit(EXIT_FAILURE);
  }
  nqueen_t nqueen = {input.n, input.verbose, 0, 0};
  solve(&nqueen);
  printf("%d solutions, with %d fundamental solutions\n",
      nqueen.num_solutions, nqueen.num_fundamental);
  return 0;
}

void solve(nqueen_t *nqueen) {
  assert(1 <= nqueen->n);
  search_t srch = {{0}, {{0}}, {0}};
  search(nqueen, &srch, 0);
}

void search(nqueen_t *nqueen, search_t *srch, int row) {
  const int n = nqueen->n;
  if (n <= row) { // DFS reaches bottom.
    int cols[N_MAX];
    bits2indices(srch->col_bits, cols, n);
    if (is_fundamental(cols, n)) {
      solution_group_t sg;
      expand(cols, n, &sg);
      nqueen->num_fundamental += 1;
      nqueen->num_solutions += sg.num;
      if (nqueen->verbose_output) {
        for (int i = 0; i < sg.num; ++i) {
          print_solution_graphic(sg.solutions[i], n);
          print_solution(sg.solutions[i], n);
          putchar(CHAR_NEWLINE);
        }
        printf("----------------\n\n");
      }
    }
  }
  const int valid_bits = (1 << n) - 1;
  int *limits = srch->limits[row];
  int *mask = srch->masks + row;
  if (row == 0 && 1 < n && n % 2 == 1) {
    // Never search position (0, n / 2) for odd n. In this
    // case, there must be at least two other queens at the
    // outer circle and closer to corner. Thus this case
    // shall be covered by some preceding case.
    *mask |= 1 << (n / 2);
  }
  int avail_bits = ~(
      limits[R_CPR] | limits[R_COL] | limits[R_CMR]);
  avail_bits &= ~(*mask);
  int col_bit = avail_bits & -avail_bits;
  while (col_bit & valid_bits) {
    srch->col_bits[row] = col_bit;
    int *next_limits = srch->limits[row + 1];
    next_limits[R_CPR] = (limits[R_CPR] | col_bit) >> 1;
    next_limits[R_COL] = limits[R_COL] | col_bit;
    next_limits[R_CMR] = (limits[R_CMR] | col_bit) << 1;
    search(nqueen, srch, row + 1);
    if (row == 0) {
      symmetry_mask(srch->masks, n, 0, msb(col_bit));
    }
    avail_bits &= ~(col_bit | *mask);
    col_bit = avail_bits & -avail_bits;
  }
}

bool is_nonsymmetric_c0_fundamental(int *rot_pos) {
  int c0_cnt = 1;
  c0_cnt += (rot_pos[0] == rot_pos[1]);
  c0_cnt += (rot_pos[0] == rot_pos[2]);
  c0_cnt += (rot_pos[0] == rot_pos[3]);
  if (c0_cnt == 1) {
    return true;
  }
  if (c0_cnt == 3) {
    return rot_pos[0] != rot_pos[1];
  }
  // c0_cnt == 2
  if (rot_pos[0] == rot_pos[2]) {
    return rot_pos[1] < rot_pos[3];
  }
  return rot_pos[0] == rot_pos[1];
}

bool is_nonsymmetric_inner_fundamental(int *rot_pos,
    bool rot4_sym) {
  if (!rot4_sym) {
    // Rot2 Symmetry broken into nonsymmetry.
    if (rot_pos[0] != rot_pos[2]) {
      return rot_pos[0] < rot_pos[2];
    } else {
      return rot_pos[1] < rot_pos[3];
    }
  }
  // Rot4 Symmetry broken into nonsymmetry.
  int min_pos = 0, min_pos_2 = -1;
  int min_cnt = 1;
  for (int i = 1; i < ROT_SYMMETRY; ++i) {
    if (rot_pos[i] < rot_pos[min_pos]) {
      min_pos = i;
      min_cnt = 1;
    } else if (rot_pos[i] == rot_pos[min_pos]) {
      min_pos_2 = i;
      ++min_cnt;
    }
  }
  if (min_cnt == 1) {
    return min_pos == 0;
  }
  if (min_cnt == 3) {
    return rot_pos[0] != rot_pos[min_pos];
  }
  // min_cnt == 2
  if (min_pos_2 == min_pos + 1) {
    return min_pos == 0;
  }
  return min_pos == 0 && rot_pos[1] < rot_pos[3];
}

bool is_fundamental(int *cols, int n) {
    if (1 == n) {
      return true;
    }
    int rows[N_MAX];
    cols2rows(cols, rows, n);
    // No rotation companions.
    // Need to exclude mirror companions.
    // Note: 0 <= cols[0] < n / 2 (even if n is odd)
    if (cols[0] == 0) {
      return rows[1] < cols[1];
    }
    // No mirror companions.
    // Need to exclude rotation companions.
    int rot_pos[ROT_SYMMETRY] = {cols[0], rows[n - 1],
      n - 1 - cols[n - 1], n - 1 - rows[0]};
    bool rot2_sym = false, rot4_sym = false;
    if (rot_pos[0] == rot_pos[2]
        && rot_pos[1] == rot_pos[3]) {
      rot2_sym = true;
      rot4_sym = (rot_pos[0] == rot_pos[1]);
    }
    if (!rot2_sym) {
      return is_nonsymmetric_c0_fundamental(rot_pos);
    }
    // Check rotation symmetry from outer circle inward.
    for (int i = 1; i < n / 2; ++i) {
      rot_pos[0] = cols[i];
      rot_pos[1] = rows[n - 1 - i];
      rot_pos[2] = n - 1 - cols[n - 1 - i];
      rot_pos[3] = n - 1 - rows[i];
      if (rot_pos[0] == rot_pos[2]
          && rot_pos[1] == rot_pos[3]) {
        // Rot2 symmetry kept.
        if (rot_pos[0] != rot_pos[1] && rot4_sym) {
          // Rot4 symmetry broken into rot2 symmetry.
          if (rot_pos[0] < rot_pos[1]) {
            return false;
          }
          rot4_sym = false;
        }
      } else {
        // Rot4/rot2 Symmetry broken into nonsymmetry.
        return is_nonsymmetric_inner_fundamental(
            rot_pos, rot4_sym);
      }
    }
    // A symmetric solution. Thus fundamental.
    return true;
}

void expand(const int *cols, int n, solution_group_t *sg) {
  copy_solution(cols, sg->solutions[0], n);
  if (1 == n) {
    sg->num = 1;
    return;
  }
  int cnt_rot = 1;
  rotate(cols, sg->solutions[cnt_rot], n);
  while (cnt_rot < ROT_SYMMETRY && !solutions_eq(cols,
        sg->solutions[cnt_rot], n)) {
    ++cnt_rot;
    if (cnt_rot < ROT_SYMMETRY) {
      rotate(sg->solutions[cnt_rot - 1],
          sg->solutions[cnt_rot], n);
    }
  }
  mirror(cols, sg->solutions[cnt_rot], n);
  if (2 <= cnt_rot && solutions_eq(sg->solutions[cnt_rot],
        sg->solutions[1], n)) {
    sg->num = cnt_rot;
    return;
  }
  for (int i = 1; i < cnt_rot; ++i) {
    mirror(sg->solutions[i], sg->solutions[cnt_rot + i], n);
  }
  sg->num = cnt_rot * 2;
}

void copy_solution(const int *from, int *to, int n) {
  for (int i = 0; i < n; ++i) {
    to[i] = from[i];
  }
}

void symmetry_mask(int *masks, int n, int row, int col) {
  masks[row] |= 1 << col; // (row, col)
  masks[row] |= 1 << (n - 1 - col);
  // ----
  masks[col] |= 1 << (n - 1 - row);
  masks[col] |= 1 << row;
  // ----
  masks[n - 1 - row] |= 1 << (n - 1 - col);
  masks[n - 1 - row] |= 1 << col;
  // ----
  masks[n - 1 - col] |= 1 << row;
  masks[n - 1 - col] |= 1 << (n - 1 - row);
}

// Cloclwise rotation.
void rotate(const int *from, int *to, int n) {
  for (int r = 0; r < n; ++r) {
    int c = from[r];
    to[c] = n - 1 - r;
  }
}

// Vertical mirror.
void mirror(const int *from, int *to, int n) {
  for (int r = 0; r < n; ++r) {
    to[r] = n - 1 - from[r];
  }
}

bool solutions_eq(const int *b1, const int *b2, int n) {
  for (int r = 0; r < n; ++r) {
    if (b1[r] != b2[r]) {
      return false;
    }
  }
  return true;
}

void bits2indices(const int *bits, int *indices, int n) {
  for (int i = 0; i < n; ++i) {
    int m = msb(bits[i]);
    assert(0 <= m && m < n);
    indices[i] = m;
  }
}

// Most significant bit.
int msb(unsigned u) {
  int m = -1;
  while (u) {
    ++m;
    u >>= 1;
  }
  return m;
}

void cols2rows(const int *cols, int *rows, int n) {
  for (int r = 0; r < n; ++r) {
    int c = cols[r];
    assert(0 <= c && c < n);
    rows[c] = r;
  }
}

// Copied from 8q.c/extension.c
user_input_t get_user_input(int argc, char *argv[]) {
  assert(argv);
  user_input_t input = {false, "", 0, false};
  if (argc != ARGC_QUIET && argc != ARGC_VERBOSE) {
    sprintf(input.err, "wrong number of arguments");
    return input;
  }
  if (argc == ARGC_VERBOSE) {
    const char *opt = argv[ARG_VERBOSE_IDX];
    assert(opt);
    if (strcmp(opt, ARG_VERBOSE) != 0) {
      sprintf(input.err, "%s is not a valid option", opt);
      return input;
    }
    input.verbose = true;
  }
  const char *n_str = argv[argc - 1];
  assert(n_str);
  // `sscanf` will read "%d" from strings like "8q".
  // Check manually that the string contains only digits.
  if (!is_digit_str(n_str)
      || sscanf(n_str, "%d", &input.n) != 1) {
    sprintf(input.err, "last argument should be integer N");
    return input;
  }
  if (input.n < N_MIN || N_MAX < input.n) {
    sprintf(input.err, "argument N not in range");
    return input;
  }
  input.valid = true;
  return input;
}

// Copied from 8q.c/extension.c
bool is_digit_str(const char *s) {
  assert(s);
  char c;
  while ((c = *s++)) {
    if (!isdigit(c)) {
      return false;
    }
  }
  return true;
}

// Copied from 8q.c/extension.c
void print_solution(int *cols, int n) {
  assert(1 <= n);
  char str[N_MAX + 1] = {0};
  for (int row = 0; row < n; ++row) {
    const int col = cols[row];
    int str_row = n - row;
    if (str_row < NUM_DIGITS) {
      str[col] = str_row + CHAR_ZERO;
    } else {
      str[col] = str_row - NUM_DIGITS + CHAR_A;
    }
  }
  for (int col = 0; col < n; ++col) {
    putchar(str[col]);
    putchar(CHAR_SPACE);
  }
  putchar(CHAR_NEWLINE);
}

// Copied from 8q.c/extension.c
void print_solution_graphic(int *cols, int n) {
  assert(1 <= n);
  neillcol colors[BOARD_COLORS] = {yellow, magenta};
  for (int row = 0; row < n; ++row) {
    const int col = cols[row];
    for (int i = 0; i < n; ++i) {
      neillbgcol(colors[(row + i) % BOARD_COLORS]);
      if (i == col) {
        putchar(CHAR_QUEEN_1);
        putchar(CHAR_QUEEN_2);
      } else {
        putchar(CHAR_SPACE);
        putchar(CHAR_SPACE);
      }
    }
    neillreset();
    putchar(CHAR_NEWLINE);
  }
}

// Function copied from Neill
/* Issue ANSI Codes change foreground colour */
void neillfgcol(const neillcol c) {
   printf("\033[%dm", c);
}

// Function copied from Neill
/* Issue ANSI Codes to change background colour */
void neillbgcol(const neillcol c) {
   neillfgcol(c+BACKGROUND);
}

// Function copied from Neill
/* Issue ANSI Codes to reset text/colour styles */
/* Equivalent to running the command 'reset' in the terminal
 */
void neillreset(void) {
   printf("\033[0m");
}

void test(void) {
  {
    int s1[5] = {0, 2, 4, 1, 3}; // 52413
    int s1_rot[5] = {4, 1, 3, 0, 2}; // 24135
    int s1_mirr[5] = {4, 2, 0, 3, 1};
    int s[5];
    assert(solutions_eq(s1, s1, 5));
    assert(!solutions_eq(s1, s1_mirr, 5));
    rotate(s1, s, 5);
    assert(solutions_eq(s1_rot, s, 5));
    mirror(s1, s, 5);
    assert(solutions_eq(s1_mirr, s, 5));
  } {
    int cols[5] = {0, 2, 4, 1, 3}; // 52413
    int rows[5] = {0, 3, 1, 4, 2};
    int buf[5];
    cols2rows(cols, buf, 5);
    assert(solutions_eq(buf, rows, 5));
  } {
    assert(msb(1) == 0);
    assert(msb(1 << 3) == 3);
    assert(msb(3 << 3) == 4);
  } {
    int masks[5] = {0};
    symmetry_mask(masks, 5, 0, 1);
    assert(masks[0] == 2 + 8);
    assert(masks[1] == 1 + 16);
    assert(masks[2] == 0);
    assert(masks[3] == 1 + 16);
    assert(masks[4] == 2 + 8);
  }
}
