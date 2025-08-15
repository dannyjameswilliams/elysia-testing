def test_create_tools_simple():

    from elysia import tool

    @tool
    async def add1(x: int, y: int) -> int:
        """
        Return the sum of two numbers.
        """
        return x + y

    from elysia import Tree

    tree = Tree()
    tree.add_tool(add1)

    response, objects = tree.run("What is 1123 + 48332?")

    assert str(1123 + 48332) in response

    tree = Tree()

    @tool(tree=tree, branch_id="base")
    async def add2(x: int, y: int) -> int:
        return x + y

    @tool
    async def calculate_two_numbers(x: int, y: int):
        """
        This function calculates the sum, product, and difference of two numbers.
        """
        yield {
            "sum": x + y,
            "product": x * y,
            "difference": x - y,
        }
        yield f"I just performed some calculations on {x} and {y}."

    tree = Tree()
    tree.add_tool(calculate_two_numbers)

    response, objects = tree.run("What is 1123 + 48332?")

    env = tree.tree_data.environment.environment
    assert "calculate_two_numbers" in env
    assert "default" in env["calculate_two_numbers"]

    result = env["calculate_two_numbers"]["default"][0]
    assert "sum" in result["objects"][0]
    assert result["objects"][0]["sum"] == 1123 + 48332
    assert result["objects"][0]["product"] == 1123 * 48332
    assert result["objects"][0]["difference"] == 1123 - 48332

    from math import prod
    from elysia import Error

    @tool
    async def perform_mathematical_operations(
        numbers: list[int | float], operation: str = "sum"
    ):
        """
        This function calculates a mathematical operation on the `numbers` list.
        The `numbers` input must be a list of integers or floats.
        The `operation` input must be one of: "sum" or "product". These are the only options.
        """

        if operation == "sum":
            yield sum(numbers)
        elif operation == "product":
            yield prod(numbers)
            # This will return an error back to the decision tree
            yield Error(
                f"You picked the input {operation}, but it was not in the available operations: 'sum' or 'product'"
            )
            return  # Then return out of the tool early

        yield f"I just performed a {operation} on {numbers}."

    tree = Tree()
    tree.add_tool(perform_mathematical_operations)

    tree("What is 2379 x 234 x 213 x 3?")

    env = tree.tree_data.environment.environment
    result = env["perform_mathematical_operations"]["default"][0]
    assert result["objects"][0]["tool_result"] == 2379 * 234 * 213 * 3
