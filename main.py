import machine

if __name__ == "__main__":
    x = machine.StateMachine({}, dict(), None, {}, {})
    x.upload_automata('input.json')
    x.make_tex('new')
    x.remove_epsilon()
    x.make_tex('new1')
    x.make_unique_path()
    x.make_tex('new2')
    x.prepare_files()


