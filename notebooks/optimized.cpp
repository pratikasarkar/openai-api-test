
#include <iostream>
#include <iomanip>
#include <chrono>

// Function calculates the result based on given iterations and parameters
double calculate(int iterations, double param1, double param2) {
    double result = 1.0;
    for (double i = 1; i <= iterations; ++i) {
        double j1 = i * param1 - param2;
        result -= (1/j1);
        double j2 = i * param1 + param2;
        result += (1/j2);
    }
    return result;
}

int main() {
    // Get the start time
    auto start_time = std::chrono::high_resolution_clock::now();

    // Calculate the result
    double result = calculate(100000000, 4.0, 1.0) * 4;

    // Get the end time
    auto end_time = std::chrono::high_resolution_clock::now();

    // Calculate the execution time
    std::chrono::duration<double> execution_time = end_time - start_time;

    // Print the result with 12 decimal places
    std::cout << "Result: " << std::fixed << std::setprecision(12) << result << std::endl;

    // Print the execution time in seconds with 6 decimal places
    std::cout << "Execution Time: " << std::fixed << std::setprecision(6) << execution_time.count() << " seconds" << std::endl;

    return 0;
}
