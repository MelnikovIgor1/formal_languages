import machine

if __name__ == "__main__":
    x = machine.StateMachine({}, dict(), None, {}, {})
    x.upload_machine('input.json')

    y = dict()

    for node in x.nodes:
        y.update({node: 1 if node in x.final else 0})

    print(x._make_state_enumeration())

    # x.get_regular('reg')

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

