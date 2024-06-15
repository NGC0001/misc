use std::env;

fn calculate_next(s: &String) -> Vec<usize> {
    let chars: Vec<char> = s.chars().collect();
    let mut next: Vec<usize> = vec![0; chars.len()];
    let mut j: i32 = 0;
    for i in 1..chars.len() {
        while 0 <= j && chars[i] != chars[j as usize] {
            if j <= 0 {
                j = -1;
            } else {
                j = next[j as usize - 1] as i32;
            }
        }
        j += 1;
        next[i] = j as usize;
    }
    next
}

// check whether a string is made up of repeating substrings
fn is_cyclic(s: &String) -> bool {
    let next = calculate_next(s);
    println!("{next:?}");
    let len = next.len();
    1 < len && 0 < next[len - 1] && len % (len - next[len - 1]) == 0
}

fn main() {
    let args: Vec<String> = env::args().collect();
    if args.len() != 2 {
        let bin = &args[0];
        println!("Usage: {bin} STR");
        return;
    }
    let cyclic: bool = is_cyclic(&args[1]);
    println!("{cyclic}");
}
