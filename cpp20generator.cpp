// https://en.cppreference.com/w/cpp/language/coroutines

#include <coroutine>
#include <cstdint>
#include <exception>
#include <iostream>

template<typename T, typename... Args>
concept ConstructibleFrom = requires (Args&&... args) {
  T{std::forward<Args>(args)...};
};

template<typename T>
class Generator {
  public:
    class promise_type;
    using handle_type = std::coroutine_handle<promise_type>;

    class promise_type {
      public:
        Generator get_return_object() {
          return Generator{handle_type::from_promise(*this)};
        }

        std::suspend_always initial_suspend() noexcept { return {}; }
        std::suspend_always final_suspend() noexcept { return {}; }
        void return_void() {}
        void unhandled_exception() { exception_ = std::current_exception(); }

        template<typename... Args> requires ConstructibleFrom<T, Args...>
        std::suspend_always yield_value(Args&&... args) {
          clear_value();
          dummy_.~Dummy();
          new (&value_) T{std::forward<Args>(args)...};
          has_value_ = true;
          return {};
        }

        ~promise_type() {
          clear_value();
          dummy_.~Dummy();
        }

      private:
        void clear_value() {
          if (has_value_) {
            value_.~T();
            has_value_ = false;
            new (&dummy_) Dummy{};
          }
        }

        struct Dummy {};
        union {
          Dummy dummy_{};
          T value_;
        };
        bool has_value_{false};

        std::exception_ptr exception_{};

      friend class Generator;
    };

    explicit Generator(handle_type h): h_{h} {}
    ~Generator() { h_.destroy(); }

    explicit operator bool() {
      fill();
      return !h_.done();
    }

    T operator()() {  // TODO: T may not be movable.
      fill();
      T v{std::move(h_.promise().value_)};
      h_.promise().has_value_ = false;
      new (&h_.promise().dummy_) promise_type::Dummy{};
      full_ = false;
      return std::move(v);
    }

  private:
    void fill() {
      if (!full_) {
        h_();
        if (h_.promise().exception_) {
          std::rethrow_exception(h_.promise().exception_);
        }
        full_ = true;
      }
    }

    handle_type h_;
    bool full_{false};
};

Generator<std::uint64_t> range(std::uint64_t n) {
  for (std::uint64_t i = 0; i < n; ++i) {
    co_yield i;
  }
}

int main() try {
  auto gen = range(10);
  while (gen) {
    std::cout << gen() << '\n';
  }
  return 0;
} catch (const std::exception& e) {
  std::cerr << "exception: " << e.what() << '\n';
} catch (...) {
  std::cerr << "unknown exception\n";
}
