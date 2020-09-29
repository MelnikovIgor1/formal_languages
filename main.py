import machine

if __name__ == "__main__":
    x = machine.StateMachine({}, dict(), None, {}, {})
    x.upload_automata('input.json')

    x.make_tex('start')
    x.make_0_1_edges()
    x.make_tex('make_0_1_edges')
    x.remove_epsilon()
    x.make_tex('remove_epsilon')
    x.make_unique_path()
    x.make_tex('make_unique_path')
    x.make_final()
    x.make_tex('make_final')
    x.invert_finite()
    x.make_tex('invert_finite')
    x.remove_all()

    x.get_regular('reg')

    # x.make_tex('1')
    # x.make_0_1_edges()
    # x.make_tex('2')
    # x.remove_epsilon()
    # x.make_tex('3')
    # x.make_unique_path()
    # x.make_tex('4')
    # x.make_final()
    # x.make_tex('5')

    x.prepare_files()

    # x.get_invert_language('reg')
    # x.prepare_files()

