#include <concepts>
#include <coroutine>
#include <cstdint>
#include <exception>
#include <iostream>
#include <stdexcept>
#include <utility>

struct Sideway {
  struct promise_type;
  using handle_type = std::coroutine_handle<promise_type>;

  struct promise_type {
    Sideway get_return_object() {
      auto h = handle_type::from_promise(*this);
      return Sideway{h};
    }

    std::suspend_never initial_suspend() { return {}; }
    std::suspend_always final_suspend() noexcept { return {}; }
    void unhandled_exception() {}
    void return_void() {}
  };

  handle_type h_;
};

bool SidewayReturn{false};

Sideway
another() {
  std::cout << "into another" << std::endl;
  while (!SidewayReturn) {
    std::cout << "another to suspend" << std::endl;
    co_await std::suspend_always{};
    std::cout << "another resumed" << std::endl;
  }
  std::cout << "another final suspension" << std::endl;
}

auto another_handle = another().h_;

struct suspend_always {
  constexpr bool await_ready() const noexcept { return false; }
  void await_suspend(std::coroutine_handle<> h) const noexcept {
    std::cout << "in suspend_always.await_suspend() , handle = " << *reinterpret_cast<std::uintptr_t*>(&h)
      // << " , h.promise().value_ = " << h.promise().value_
      << std::endl;
    // h.promise().value_ += 0;
  }
  constexpr void await_resume() const noexcept {}
};

struct yield_suspend {
  constexpr bool await_ready() const noexcept { return false; }
  decltype(another_handle) await_suspend(std::coroutine_handle<> h) const noexcept {
    std::cout << "in yield_suspend.await_suspend() , to return another_handle : " << *reinterpret_cast<std::uintptr_t*>(&another_handle)
      << std::endl;
    return another_handle;
  }
  constexpr void await_resume() const noexcept {}
};

template<typename T>
struct Generator {
  struct promise_type;
  using handle_type = std::coroutine_handle<promise_type>;

  struct promise_type {
    T value_{1};
    std::exception_ptr exception_;

    promise_type() {
      std::cout << "Promise object created at " << reinterpret_cast<std::uintptr_t>(this) << " , with ++value_ = " << ++value_ << std::endl;
    }
    ~promise_type() {
      std::cout << "Promise object destroyed, with ++_value = " << ++value_ << std::endl;
    }

    Generator get_return_object() {
      std::cout << "promise.get_return_object() called, with ++value_ = " << ++value_ << std::endl;
      return Generator(handle_type::from_promise(*this));
    }
    std::suspend_never initial_suspend() {
      std::cout << "promise.initial_suspend() called. no suspension expected. ++value = " << ++value_ << std::endl;
      return {};
    }
    suspend_always final_suspend() noexcept {
      std::cout << "promise.final_suspend() called. suspension expected." << std::endl;
      return {};
    }
    void unhandled_exception() {
      std::cout << "promise.unhandled_exception() called." << std::endl;
      exception_ = std::current_exception();
    }
    template<std::convertible_to<T> From> // C++20 concept
    yield_suspend yield_value(From &&from) {
      std::cout << "promise.yield_value() called . (before assignment) ++value_ = " << ++value_ << " , to assign " << from << std::endl;
      value_ = std::forward<From>(from);
      return {};
    }
    void return_void() {}
  };

  handle_type h_;

  Generator(handle_type h) : h_(h) {
    std::cout << "Return object (the generator) created. sizeof(size_t) = " << sizeof(size_t)
      << " , sizeof(handle<P>) = " << sizeof(handle_type)
      << " , sizeof(handle<>) = " << sizeof(std::coroutine_handle<>)
      << " , sizeof(std::uintptr_t) = " << sizeof(std::uintptr_t)
      << " , handle = " << *reinterpret_cast<std::uintptr_t*>(&h_)
      << " , handle.done() = " << h_.done()
      << std::endl;
    print_value_at_handle(h_);
  }
  ~Generator() {
    std::cout << "entering generator destructor." << std::endl;
    print_value_at_handle(h_);
    std::cout << "to call h_.destroy()" << std::endl;
    h_.destroy();
    std::cout << "h_.destroy() called." << std::endl;
    print_value_at_handle(h_);
    // std::cout << "resume handle after destroyed." << std::endl;
    // h_();
    // std::cout << "destroy handle twice" << std::endl;
    // h_.destroy();
    std::cout << "test h_.done() after destroyed: " << h_.done() << std::endl;
    std::cout << "Return object (the generator) destroyed." << std::endl;
  }
  explicit operator bool() {
    // fill();
    return !h_.done();
  }
  T operator()() {
    fill();
    full_ = false;
    return std::move(h_.promise().value_);
  }

private:
  bool full_ = false;

  void fill() {
    if (!full_) {
      std::cout << "to resume handle execution." << std::endl;
      print_value_at_handle(h_);
      h_();
      std::cout << "from suspended handle." << std::endl;
      if (h_.promise().exception_) {
        std::cout << "exception found in fill(). h_.done() = " << h_.done() << std::endl;
        // std::cout << "try to resume handle after exception found in fill()." << std::endl;
        // h_();
        // std::cout << "try to neglect exception in fill()." << std::endl;
        std::rethrow_exception(h_.promise().exception_);
      }
      full_ = true;
    }
  }
  void print_value_at_handle(handle_type h, bool print = true) {
    if (!print) {
      return;
    }
    using pointer_type = uint32_t*;
    pointer_type ptr = *reinterpret_cast<pointer_type*>(&h);
    std::cout << "  value at handle:" << std::endl;
    for (int i = -2; i < 6; ++i) {
      std::cout << "    " << i << " *(" << reinterpret_cast<std::uintptr_t>(ptr + i) << ")=" << size_t(*(ptr + i)) << std::endl;
    }
  }
};

Generator<unsigned>
counter() {
  int _gInt;
  std::cout << "Coroutine int address (before 1st suspension): " << reinterpret_cast<std::uintptr_t>(&_gInt) << std::endl;
  // std::cout << "To throw before 1st suspension" << std::endl;
  // throw std::runtime_error{"in cortoutine before 1st suspension"};
  co_await suspend_always{};
  std::cout << "Coroutine int address (after 1st suspension): " << reinterpret_cast<std::uintptr_t>(&_gInt) << std::endl;
  // std::cout << "To throw after 1st suspension" << std::endl;
  // throw std::runtime_error{"in cortoutine after 1st suspension"};
  for (unsigned i = 0; i < 3; ++i) {
    if (i == 0) {
      co_yield i;
      i += 1;
    } else {
      co_yield i;
    }
  }
}

int _GlobalInt;

int main() try {
  std::cout << "Data int address: " << reinterpret_cast<std::uintptr_t>(&_GlobalInt) << std::endl;

  int _tmpInt;
  std::cout << "Stack int address: " << reinterpret_cast<std::uintptr_t>(&_tmpInt) << std::endl;

  int *_tmpIntPtr = new int;
  std::cout << "Heap int address: " << reinterpret_cast<std::uintptr_t>(_tmpIntPtr) << std::endl;
  delete _tmpIntPtr; _tmpIntPtr = nullptr;

  auto gen = counter();
  std::cout << "After generator creation. Generator address: " << reinterpret_cast<std::uintptr_t>(&gen) << std::endl;

  while (gen) {
    auto v = gen();
    std::cout << "counter: " << v << std::endl;
  }

  std::cout << "main exit normally." << std::endl;
  return 0;
} catch (const std::runtime_error& e) {
  std::cout << "std::runtime_error from main: " << e.what() << std::endl;
  return 1;
} catch (...) {
  std::cout << "exceptions from main" << std::endl;
  return -1;
}
