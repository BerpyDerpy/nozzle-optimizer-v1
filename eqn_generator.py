import random


class EquationGenerator():
    def __init__(self):
        self.problems = []

    def generate_linear_equation(self):
        # ax + b = c
        a = random.randint(1, 5)
        b = random.randint(-15, 15)
        x = random.randint(-10, 10)
        c = a * x + b

        return {'a': a,
                'b': b,
                'c': c,
                'x': x,
                'equation': f"{a}x + {b} = {c}" if b >= 0 else f"{a}x - {abs(b)} = {c}"}

    def solve(self, problem):
        # ax = c
        a, b, c, x = problem['a'], problem['b'], problem['c'], problem['x']
        equation = problem['equation']
        steps = []
        steps.append(f"solve_and_verify: {equation}")
        if b >= 0:
            steps.append(f"{a}x = {c} - {b}")
            steps.append(f"{a}x = {c - b}")
        else:
            steps.append(f"{a}x = {c} + {abs(b)}")
            steps.append(f"{a}x = {c + abs(b)}")

        steps.append(f"x = {c - b}/{a}")
        steps.append(f"x = {x}")
        if b >= 0:
            steps.append(f"Verify:\n"
                         f"substitute x = {x} into {equation}:\n"
                         f"{a}({x}) + {b}\n{a * x} + {b}\n{a * x + b}\n"
                         f"equation_gives: {a * x + b}\n"
                         f"target_value: {c}\n"
                         f"verified: {a * x + b} = {c} ✓")
        else:
            steps.append(f"Verify:\n"
                         f"substitute x = {x} into {equation}:\n"
                         f"{a}({x}) - {abs(b)}\n{a * x} - {abs(b)}\n{a * x + b}\n"
                         f"equation_gives: {a * x + b}\n"
                         f"target_value: {c}\n"
                         f"verified: {a * x + b} = {c} ✓")
        return steps

    def generate_single_problem(self):
        problem = self.generate_linear_equation()
        steps = self.solve(problem)

        formatted = '\n'.join(steps)
        formatted += "\n" + "=" * 50 + "\n"
        return formatted

    def generate_dataset(self, num):
        dataset = []

        for i in range(num):
            prob = self.generate_single_problem()
            dataset.append(prob)

            if (i + 1) % 1000 == 0:
                print(f"Generated {i + 1} problems...")

        return dataset

    def save_dataset(self, dataset, filename):

        with open(filename, 'w', encoding='utf-8') as f:
            for prob in dataset:
                f.write(prob)

        print(f"Saved {len(dataset)} problems to {filename}")


if __name__ == "__main__":
    generator = EquationGenerator()

    dataset = generator.generate_dataset(10000)
    generator.save_dataset(dataset, "linearEQNs.txt")
