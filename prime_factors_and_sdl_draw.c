#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <assert.h>
#include <math.h>

#include <SDL.h>

/* ********************************
 * To avoid directly lining up for powers of 2,
 * even number of factor 2s are merged into factor 4s,
 * e.g., 96 = 3x2x2x2x2x2 -> 3x2x4x4 .
 * For 4, four spots are drawn as a square.
 *
 * For factor 2, sub-areas are drawn facing outward.
 * For other factors including 4,
 * sub-areas are drawn with the facing of its parent-area.
 * This conforms with the website:
 *     http://www.datapointed.net/visualizations/math/
 *             factorization/animated-diagrams/
 *
 * The color scheme is only a guess from the above website.
 * ******************************** */

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif
#define PI M_PI

#define EPSILON 1.0e-12

#define MAX_FACTOR_CNT 64
#define PRIME_MIN 2
#define FACTOR_TWO 2
#define FACTOR_FOUR 4

#define WINDOW_USE_RATIO 0.9
#define INCIRCLE_RATIO 0.95
#define SPOT_RATIO 0.9

#define RGB_TUPLE 3
#define RGB_HUE_CNT 6 // 3!
#define R_IDX 0
#define G_IDX 1
#define B_IDX 2
#define CLR_MIN 0
#define CLR_MAX 150

#define WHEIGHT 600
#define WWIDTH 800
#define MILLISECONDDELAY 20

/* --------------------------------
 * Some definitions and declarations from Neill.
 *     https://github.com/csnwc/Exercises-In-C
 *         /Code/Week5/SDL/neillsdl2.h
 * -------------------------------- */
typedef struct {
  SDL_bool finished;
  SDL_Window *win;
  SDL_Renderer *renderer;
  SDL_Texture *display;
} SDL_Simplewin;
// --------------------------------
void Neill_SDL_Init(SDL_Simplewin *sw);
void Neill_SDL_Events(SDL_Simplewin *sw);
void Neill_SDL_SetDrawColour(SDL_Simplewin *sw,
    Uint8 r, Uint8 g, Uint8 b);
void Neill_SDL_RenderFillCircle(SDL_Renderer *rend,
    int cx, int cy, int r);
void Neill_SDL_UpdateScreen(SDL_Simplewin *sw);
/* --------------------------------
 * End of definitions and declarations from Neill.
 * -------------------------------- */

// Positions are relative to window center.
// Positive means rightward(for x) or upward(for y).
// Conversion needed when translated into SDL coordinate.
typedef struct {
  double x;
  double y;
} pos_t;

typedef unsigned char color_t;
typedef color_t rgb_arr[RGB_TUPLE];

typedef struct {
  pos_t pos;
  double r;
  rgb_arr color;
} spot_t;

typedef struct {
  pos_t center;
  double radius;
  double orient;
  double angular_radius;
} drawing_area_t;

void test(void);
void factor_and_draw(int num);
int do_factoring(int num, int *factors, int max_cnt);
void invert_array(int arr[], int len);
int merge_twos(int *factors, int cnt);
drawing_area_t get_circle_from_window(
    int height, int width);
void calc_spots_pos(const drawing_area_t *circle, int cnt_f,
    const int *factors, int num, spot_t *spots);
drawing_area_t cut_fan_out_of(const drawing_area_t *circle,
    int fctr, int idx);
drawing_area_t get_incircle_of(const drawing_area_t *fan);
bool float_eq(double d1, double d2);
bool float_le(double d1, double d2);
void colorize_spots(spot_t *spots, int num);
void draw_spots(SDL_Simplewin *sw, spot_t *spots, int num);

int main(int argc, char *argv[]) {
  test();

  if (argc != 2) {
    fprintf(stderr, "usage: %s POSITIVE_NUMBER\n", argv[0]);
    exit(EXIT_FAILURE);
  }
  int num = 0;
  if (sscanf(argv[1], "%d", &num) != 1 || num < 1) {
    fprintf(stderr,
        "expect a positive integer as argument\n");
    exit(EXIT_FAILURE);
  }
  factor_and_draw(num);
  return 0;
}

void factor_and_draw(int num) {
  assert(0 < num);
  int factors[MAX_FACTOR_CNT];
  int cnt_f = do_factoring(num, factors, MAX_FACTOR_CNT);
  invert_array(factors, cnt_f); // ascending -> descending
  cnt_f = merge_twos(factors, cnt_f);

  spot_t *spots = malloc(num * sizeof(spot_t));
  assert(spots);
  drawing_area_t circle = get_circle_from_window(
      WHEIGHT, WWIDTH);
  calc_spots_pos(&circle, cnt_f, factors, num, spots);
  colorize_spots(spots, num);

  SDL_Simplewin sw;
  Neill_SDL_Init(&sw);
  draw_spots(&sw, spots, num);
  do {
    // Busy loop.
    // The coding Gods have to forgive this code.
    Neill_SDL_Events(&sw);
  } while (!sw.finished);
  SDL_Quit();
  atexit(SDL_Quit); // Is this needed?

  free(spots);
}

int do_factoring(int num, int *factors, int max_cnt) {
  assert(0 < num && factors);
  int idx = 0, fctr = PRIME_MIN;
  while (PRIME_MIN <= num) {
    while (num % fctr == 0) {
      assert(idx < max_cnt);
      factors[idx++] = fctr;
      num /= fctr;
    }
    ++fctr;
  }
  return idx;
}

void invert_array(int arr[], int len) {
  assert(arr && 0 <= len);
  int i = 0, j = len - 1;
  while (i < j) {
    int tmp = arr[i];
    arr[i] = arr[j];
    arr[j] = tmp;
    ++i;
    --j;
  }
}

int merge_twos(int *factors, int cnt) {
  assert(factors && 0 <= cnt);
  int pos = 0;
  while (pos < cnt && factors[pos] != FACTOR_TWO) {
    ++pos;
  }
  pos += (cnt - pos) % 2;
  const int num_fours = (cnt - pos) / 2;
  for (int i = 0; i < num_fours; ++i) {
    factors[pos++] = FACTOR_FOUR;
  }
  return pos;
}

drawing_area_t get_circle_from_window(
    int height, int width) {
  assert(0 < height && 0 < width);
  double half_height = height / 2.0;
  double half_width = width / 2.0;
  double radius = height < width ? half_height : half_width;
  radius *= WINDOW_USE_RATIO;
  drawing_area_t circle = {{0.0, 0.0}, radius, 0.0, PI};
  return circle;
}

void calc_spots_pos(const drawing_area_t *circle, int cnt_f,
    const int *factors, int num, spot_t *spots) {
  assert(circle &&  0 <= cnt_f && factors && 0 < num
      && spots);
  assert(float_eq(circle->angular_radius, PI));
  if (cnt_f == 0) { // No sub-areas. Settle the spot.
    assert(num == 1);
    spots->pos = circle->center;
    spots->r = circle->radius * SPOT_RATIO;
    return;
  }
  int fctr = *factors;
  int quotient = num / fctr;
  int next_fctr = 1 < cnt_f ? *(factors + 1) : 1;
  assert(1 < fctr && num % fctr == 0);
  for (int idx = 0; idx < fctr; ++idx) { // Calc sub-areas.
    drawing_area_t sub_fan = cut_fan_out_of(circle, fctr,
        idx);
    drawing_area_t incircle = get_incircle_of(&sub_fan);
    if (next_fctr != FACTOR_TWO) {
      // Facing as parent-area (effectively, facing upward).
      incircle.orient = circle->orient;
    }
    calc_spots_pos(&incircle, cnt_f - 1, factors + 1,
        quotient, spots + quotient * idx);
  }
}

drawing_area_t cut_fan_out_of(const drawing_area_t *circle,
    int fctr, int idx) {
  assert(circle && 1 < fctr && 0 <= idx && idx < fctr);
  assert(float_eq(circle->angular_radius, PI));
  drawing_area_t fan = *circle;
  fan.angular_radius = PI / fctr;
  fan.orient += idx * fan.angular_radius * 2;
  if (fctr == FACTOR_FOUR) {
    fan.orient += PI / 4.0;
  }
  return fan;
}

drawing_area_t get_incircle_of(const drawing_area_t *fan) {
  assert(fan);
  assert(float_le(fan->angular_radius, PI / 2.0));
  drawing_area_t incircle;
  incircle.orient = fan->orient; // Facing outward.
  incircle.angular_radius = PI;
  double sin_fan_ar = sin(fan->angular_radius);
  incircle.radius = fan->radius * sin_fan_ar
    / (1.0 + sin_fan_ar);
  double displacement = fan->radius - incircle.radius;
  incircle.center.x = fan->center.x
    + displacement * sin(fan->orient);
  incircle.center.y = fan->center.y
    + displacement * cos(fan->orient);
  incircle.radius *= INCIRCLE_RATIO;
  return incircle;
}

bool float_eq(double d1, double d2) {
  double mag = fmax(fabs(d1), fabs(d2));
  return fabs(d1 - d2) <= mag * EPSILON;
}

bool float_le(double d1, double d2) {
  return d1 < d2 || float_eq(d1, d2);
}

// Loop through different hues, starting from blue.
// When the number of spots is large, try to give
// adjacent spots (being adjacent on the screen, which also
// means being adjacent in the `spots` array) similar hues.
void colorize_spots(spot_t *spots, int num) {
  assert(spots && 0 < num);
  const int clr_cnt = (CLR_MAX - CLR_MIN) * RGB_HUE_CNT;
  int clr_delta = 1 + clr_cnt / num;
  rgb_arr clr = {CLR_MIN, CLR_MIN, CLR_MAX};
  int minus_idx = 2; // Blue
  int plus_idx = (minus_idx + 1) % RGB_TUPLE;
  for (int i = 0; i < num; ++i) {
    spots[i].color[R_IDX] = clr[R_IDX];
    spots[i].color[G_IDX] = clr[G_IDX];
    spots[i].color[B_IDX] = clr[B_IDX];
    int clr_v;
    if ((clr_v = clr[plus_idx]) < CLR_MAX) {
      clr_v += clr_delta;
      clr[plus_idx] = clr_v < CLR_MAX ? clr_v : CLR_MAX;
    } else {
      clr_v = clr[minus_idx] - clr_delta;
      if (CLR_MIN < clr_v) {
        clr[minus_idx] = clr_v;
      } else {
        clr[minus_idx] = CLR_MIN;
        plus_idx = (plus_idx + 1) % RGB_TUPLE;
        minus_idx = (minus_idx + 1) % RGB_TUPLE;
      }
    }
  }
}

void draw_spots(SDL_Simplewin *sw, spot_t *spots, int num) {
  assert(spots && 0 <= num);
  SDL_Delay(MILLISECONDDELAY);
  for (int i = 0; i < num; ++i) {
    Neill_SDL_SetDrawColour(sw, spots[i].color[R_IDX],
        spots[i].color[G_IDX], spots[i].color[B_IDX]);
    Neill_SDL_RenderFillCircle(sw->renderer,
        // Coordinates conversion.
        spots[i].pos.x + WWIDTH / 2.0,
        WHEIGHT / 2.0 - spots[i].pos.y,
        spots[i].r);
  }
  Neill_SDL_UpdateScreen(sw);
}

void test(void) {
  {
    int factors[4] = {1, 1, 1, 1};
    assert(do_factoring(147, factors, 4) == 3);
    assert(factors[0] == 3 && factors[1] == 7
        && factors[2] == 7 && factors[3] == 1);
  } {
    int arr[4] = {1, 3, 0, 7};
    invert_array(arr, 3);
    assert(arr[0] == 0 && arr[1] == 3
        && arr[2] == 1 && arr[3] == 7);
  } {
    int factors[4] = {3, 2, 2, 2};
    assert(merge_twos(factors, 4) == 3);
    assert(factors[0] == 3 && factors[1] == 2
        && factors[2] == 4 && factors[3] == 2);
  } {
    assert(float_eq(0.0, 0.0));
    assert(!float_eq(0.1, 0.101));
    assert(float_le(1.2, 1.2));
    assert(!float_le(-1.2, -1.3));
  } {
    drawing_area_t circle = {{0.0, 0.0}, 1.0, 0.0, PI};
    drawing_area_t fan = cut_fan_out_of(&circle, 3, 1);
    assert(float_eq(fan.center.x, 0.0));
    assert(float_eq(fan.center.y, 0.0));
    assert(float_eq(fan.radius, 1.0));
    assert(float_eq(fan.orient, 2.0 * PI / 3.0));
    assert(float_eq(fan.angular_radius, PI / 3.0));
  } {
    drawing_area_t fan = {{0.0, 0.0}, 2.0, 0.0, PI / 2.0};
    drawing_area_t incircle = get_incircle_of(&fan);
    assert(float_eq(incircle.center.x, 0.0));
    assert(float_eq(incircle.center.y, 1.0));
    assert(float_eq(incircle.radius, 1.0 * INCIRCLE_RATIO));
    assert(float_eq(incircle.orient, 0.0));
    assert(float_eq(incircle.angular_radius, PI));
  } {
    drawing_area_t circle = {{0.0, 0.0}, 2.0, 0.0, PI};
    int factors[2] = {3, 2};
    spot_t spots[6];
    calc_spots_pos(&circle, 2, factors, 6, spots);
    assert(spots[5].pos.x < 0.0);
    assert(spots[5].pos.y < 0.0);
    assert(spots[5].r < 1.0 * SPOT_RATIO);
  } {
    spot_t spots[RGB_HUE_CNT];
    colorize_spots(spots, RGB_HUE_CNT);
    assert(spots[1].color[R_IDX] == CLR_MAX);
    assert(spots[1].color[G_IDX] == CLR_MIN);
    assert(spots[1].color[B_IDX] == CLR_MAX);
    assert(spots[2].color[R_IDX] == CLR_MAX);
    assert(spots[2].color[G_IDX] == CLR_MIN);
    assert(spots[2].color[B_IDX] == CLR_MIN);
    assert(spots[3].color[R_IDX] == CLR_MAX);
    assert(spots[3].color[G_IDX] == CLR_MAX);
    assert(spots[3].color[B_IDX] == CLR_MIN);
  }
}

/* ********************************
 * Code below is copied and adapted from Neill's.
 *     https://github.com/csnwc/Exercises-In-C
 *         /Code/Week5/SDL/neillsdl2.c
 * ******************************** */

/* Do something standard everytime an error is trapped */
#define ON_ERROR(STR)                                 \
  fprintf(stderr, "\n%s: %s\n", STR, SDL_GetError()); \
  SDL_Quit();                                         \
  exit(1)

/* Set up a simple (WIDTH, HEIGHT) window.
   Attempt to hide the renderer etc. from user. */
void Neill_SDL_Init(SDL_Simplewin *sw) {
  if (SDL_Init(SDL_INIT_VIDEO) != 0) {
    ON_ERROR("Unable to initialize SDL");
  } 

  sw->finished = 0;
  sw->win= SDL_CreateWindow("SDL Window",
      SDL_WINDOWPOS_UNDEFINED,
      SDL_WINDOWPOS_UNDEFINED,
      WWIDTH, WHEIGHT,
      SDL_WINDOW_SHOWN);
  if(sw->win == NULL) {
    ON_ERROR("Unable to initialize SDL Window");
  }

  /* Change SOFTWARE -> SDL_RENDERER_SOFTWARE to
   * SDL_RENDERER ACCELERATED if you have a graphics card
   * i.e. are not using remote access */
  sw->renderer = SDL_CreateRenderer(sw->win, -1,
      SDL_RENDERER_SOFTWARE | SDL_RENDERER_TARGETTEXTURE);
  if(sw->renderer == NULL) {
    ON_ERROR("Unable to initialize SDL Renderer");
  }
  SDL_SetRenderDrawBlendMode(sw->renderer,
      SDL_BLENDMODE_BLEND);

  /* Create texture for display */
  sw->display = SDL_CreateTexture(sw->renderer,
      SDL_PIXELFORMAT_RGBA8888, SDL_TEXTUREACCESS_TARGET,
      WWIDTH, WHEIGHT);
  if(sw->display == NULL) {
    ON_ERROR("Unable to initialize SDL texture");
  }
  SDL_SetRenderTarget(sw->renderer, sw->display);

  /* Clear screen, & set draw colour to white */
  SDL_SetRenderDrawColor(sw->renderer, 255, 255, 255, 255);
  SDL_RenderClear(sw->renderer);
}

/* Housekeeping to do with the render buffer
 * & updating the screen */
void Neill_SDL_UpdateScreen(SDL_Simplewin *sw) {
  SDL_SetRenderTarget(sw->renderer, NULL);
  SDL_RenderCopy(sw->renderer, sw->display, NULL, NULL);
  SDL_RenderPresent(sw->renderer);
  SDL_SetRenderTarget(sw->renderer, sw->display);
}

/* Gobble all events & ignore most */
void Neill_SDL_Events(SDL_Simplewin *sw) {
  SDL_Event event;
  while (SDL_PollEvent(&event)) {      
    switch (event.type) {
      case SDL_QUIT:
      case SDL_MOUSEBUTTONDOWN:
      case SDL_KEYDOWN:
        sw->finished = 1;
    }
  }
}

/* Trivial wrapper to avoid complexities of
 * renderer & alpha channels */
void Neill_SDL_SetDrawColour(SDL_Simplewin *sw,
    Uint8 r, Uint8 g, Uint8 b) {
  SDL_SetRenderDrawColor(sw->renderer, r, g, b,
      SDL_ALPHA_OPAQUE);
}

/* Filled Circle centred at (cx,cy) of radius r, see :
https://en.wikipedia.org/wiki/Midpoint_circle_algorithm */
void Neill_SDL_RenderFillCircle(SDL_Renderer *rend,
    int cx, int cy, int r) {
  double dy;
  for (dy = 1; dy <= r; dy += 1.0) {
    double dx = floor(sqrt((2.0 * r * dy) - (dy * dy)));
    SDL_RenderDrawLine(rend,
        cx - dx, cy + r - dy, cx + dx, cy + r - dy);
    SDL_RenderDrawLine(rend,
        cx - dx, cy - r + dy, cx + dx, cy - r + dy);
  }
}
