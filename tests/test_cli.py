from cli import format_response


def test_format_response_includes_type_and_response():
    result = {"type": "qualitative", "response": "Some answer here."}
    output = format_response(result)
    assert "[QUALITATIVE]" in output
    assert "Some answer here." in output


def test_format_response_handles_complex_type():
    result = {"type": "complex", "response": "**Qualitative:**\nX\n\n**Quantitative:**\nY"}
    output = format_response(result)
    assert "[COMPLEX]" in output
    assert "Qualitative" in output
    assert "Quantitative" in output

def test_cli_exits_cleanly_on_exit_command(monkeypatch, capsys):
    inputs = iter(["exit"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    import cli
    
    class FakeManager:
        def handle_query(self, q):
            return {"type": "unsupported", "response": "n/a"}
    monkeypatch.setattr(cli, "build_system", lambda llm_fn: FakeManager())

    cli.main()

    captured = capsys.readouterr()
    assert "Goodbye." in captured.out


def test_cli_skips_empty_input_and_continues(monkeypatch, capsys):
    inputs = iter(["", "exit"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    import cli
    class FakeManager:
        def handle_query(self, q):
            return {"type": "unsupported", "response": "n/a"}
    monkeypatch.setattr(cli, "build_system", lambda llm_fn: FakeManager())

    cli.main()

    captured = capsys.readouterr()
    assert "Goodbye." in captured.out