#include <iostream>
#include <string>
#include <utility>
#include <vector>

template <typename C>
auto operator<<(std::ostream& os, const C& c) -> decltype(*c.begin(), *c.end(), os) {
  os << '[';
  for (const auto& v : c) {
    os << v << ',';
  }
  os << ']';
  return os;
}

// next[i]: the longest pre-post-fix of string sub[0:i+1]
// pre-post-fix: a substring which is both the prefix and postfix of its parent string
std::vector<int> calculate_next(const std::string& sub) {
  std::vector<int> next(sub.size());
  if (sub.size() <= 0) {
    return next;
  }
  next[0] = 0;
  for (int i = 1, j = 0; i < sub.size(); ++i, ++j) {
    while (0 <= j && sub[i] != sub[j]) {
      j = next[j] - 1;
    }
    next[i] = j + 1;
  }
  return next;
}

int find_substr(const std::string& str, const std::string& sub) {
  std::vector<int> next = calculate_next(sub);
  std::cout << next << std::endl;
  int len_diff = str.size() - sub.size();
  for (int i = 0, j = 0; i - j <= len_diff; ++i, ++j) {
    if (sub.size() <= j) {
      return i - j;
    }
    while (0 <= j && str[i] != sub[j]) {
      if (j == 0) {
        j = -1;
      } else {
        j = next[j - 1];
      }
    }
  }
  return -1;
}

// next_opt[i]: if str and sub do not match at str[k]/sub[i],
//              then should try to match str[k]/sub[next_opt[i]]
std::vector<int> calculate_next_opt(const std::string& sub) {
  std::vector<int> next_opt = calculate_next(sub);
  for (int i = next_opt.size() - 1; 0 < i; --i) {
    int j = next_opt[i - 1];
    while (0 <= j && sub[j] == sub[i]) {  // sub[j] will also fail to match sub[k]
      if (j == 0) {
        j = -1;
      } else {
        j = next_opt[j - 1];
      }
    }
    next_opt[i] = j;
  }
  if (0 < next_opt.size()) {
    next_opt[0] = -1;
  }
  return next_opt;
}

// optimized kmp matching, e.g., when the substring is "aaaaa"
int find_substr_opt(const std::string& str, const std::string& sub) {
  std::vector<int> next_opt = calculate_next_opt(sub);
  std::cout << next_opt << std::endl;
  int len_diff = str.size() - sub.size();
  for (int i = 0, j = 0; i - j <= len_diff; ++i, ++j) {
    if (sub.size() <= j) {
      return i - j;
    }
    while (0 <= j && str[i] != sub[j]) {
      j = next_opt[j];
    }
  }
  return -1;
}

int main(int argc, char *argv[]) {
  if (argc != 3) {
    std::cerr << "Usage: " << argv[0] << " STR SUB" << std::endl;
    return -1;
  }
  std::cout << find_substr(argv[1], argv[2]) << std::endl;
  std::cout << find_substr_opt(argv[1], argv[2]) << std::endl;
  return 0;
}
