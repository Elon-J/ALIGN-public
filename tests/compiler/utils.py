import os
import pathlib
import shutil
import json
import textwrap

my_dir = pathlib.Path(__file__).resolve().parent
pdk_path = (
    pathlib.Path(__file__).resolve().parent.parent.parent
    / "pdks"
    / "FinFET14nm_Mock_PDK"
)
config_path = pathlib.Path(__file__).resolve().parent.parent / "files"
out_path = pathlib.Path(__file__).resolve().parent / "Results"


def ota_six(name):
    netlist = textwrap.dedent(
        f"""\
        .subckt {name} ibias vccx vssx  von vin vip
        mn1 ibias ibias vssx vssx n w=360e-9 nf=2 m=8
        mn2 tail  ibias vssx vssx n w=360e-9 nf=2 m=8
        mn3 vop vip tail vssx n w=360e-9 nf=2 m=16
        mn4 von vin tail vssx n w=360e-9 nf=2 m=16
        mp5 vop vop vccx vccx p w=360e-9 nf=2 m=4
        mp6 von vop vccx vccx p w=360e-9 nf=2 m=4
        .ends {name}
    """
    )
    return netlist


def ota_dummy(name):
    netlist = textwrap.dedent(
        f"""\
        .subckt {name} ibias vccx vssx  von vin vip
        mn1 ibias ibias vssx vssx n w=360e-9 nf=2 m=8
        mn2 tail  ibias vssx vssx n w=360e-9 nf=2 m=8
        mn3 vop vip tail vssx n w=360e-9 nf=2 m=16
        mn4 von vin tail vssx n w=360e-9 nf=2 m=16
        mn3_dummy vop vop vop vssx n w=360e-9 nf=2 m=16
        mn4_dummy von von von vssx n w=360e-9 nf=2 m=16
        mp5 vop vop vccx vccx p w=360e-9 nf=2 m=4
        mp6 von vop vccx vccx p w=360e-9 nf=2 m=4
        .ends {name}
    """
    )
    return netlist


def ota_six_flip(name):
    netlist = textwrap.dedent(
        f"""\
        .subckt {name} ibias vccx vssx  von vin vip
        mn1 ibias ibias vssx vssx n w=360e-9 nf=2 m=8
        mn2 tail  ibias vssx vssx n w=360e-9 nf=2 m=8
        mn3 vop vip tail vssx n w=360e-9 nf=2 m=16
        mn4 tail vin von vssx n w=360e-9 nf=2 m=16
        mp5 vop vop vccx vccx p w=360e-9 nf=2 m=4
        mp6 von vop vccx vccx p w=360e-9 nf=2 m=4
        .ends {name}
    """
    )
    return netlist


def ring_oscillator(name):
    netlist = textwrap.dedent(
        f"""\
        .subckt inverter vi vo vssx vccx
        mp0 vo vi vcccx vccx p nfin=4 l=40n m=2
        mn0 vo vi vssx vssx n nfin=4 l=40n m=2
        .ends inverter
        .subckt {name} vo vccx vssx
        xi0 vo n1 vssx vccx inverter
        xi1 n1 n2 vssx vccx inverter
        xi2 n2 n3 vssx vccx inverter
        xi3 n3 n4 vssx vccx inverter
        xi4 n4 vo vssx vccx inverter
        .ends {name}
    """
    )
    return netlist


def ring_oscillator_flat(name):
    netlist = textwrap.dedent(
        f"""\
        .subckt {name} vo vccx vssx
        mp0 vo n1 vccx vccx p nfin=4 l=40n m=2
        mn0 vo n1 vssx vssx n nfin=4 l=40n m=2
        mp1 n1 n2 vccx vccx p nfin=4 l=40n m=2
        mn1 n1 n2 vssx vssx n nfin=4 l=40n m=2
        mp2 n2 n3 vccx vccx p nfin=4 l=40n m=2
        mn2 n2 n3 vssx vssx n nfin=4 l=40n m=2
        mp3 n3 n4 vccx vccx p nfin=4 l=40n m=2
        mn3 n3 n4 vssx vssx n nfin=4 l=40n m=2
        mp4 n4 v0 vccx vccx p nfin=4 l=40n m=2
        mn4 n4 v0 vssx vssx n nfin=4 l=40n m=2
        .ends {name}
    """
    )
    return netlist


def variable_gain_amplifier_equal(name):
    netlist = textwrap.dedent(
        f"""\
        .subckt {name} vmirror_vga s0 s1 s2 s3 vin1 vin2 vout_vga1 vout_vga2 vps vgnd
        .param nfpf_sw=72 nfpf_cm=72 nfpf_dp=48 rl=400
        M03 vmirror_vga vmirror_vga vgnd vgnd nfet nfin=nfpf_cm m=1 nf=1
        M02 net3p vmirror_vga vgnd vgnd nfet nfin=nfpf_cm m=1  nf=1
        M01 vout_vga2 vin2 net3 vgnd nfet nfin=nfpf_dp m=1 nf=1
        M00 vout_vga1 vin1 net3 vgnd nfet nfin=nfpf_dp
        Msw0 net3 s0 net3p vgnd nfet l=0.014u nfin=nfpf_sw
        Msw1 net5 s1 net5p vgnd nfet l=0.014u nfin=nfpf_sw
        M12 net5p vmirror_vga vgnd vgnd nfet nfin=nfpf_cm
        M11 vout_vga2 vin2 net5 vgnd nfet nfin=nfpf_dp
        M10 vout_vga1 vin1 net5 vgnd nfet nfin=nfpf_dp
        Msw2 net4 s2 net4p vgnd nfet l=0.014u nfin=nfpf_sw
        M22 net4p vmirror_vga vgnd vgnd nfet nfin=nfpf_cm
        M21 vout_vga2 vin2 net4 vgnd nfet nfin=nfpf_dp
        M20 vout_vga1 vin1 net4 vgnd nfet nfin=nfpf_dp
        Msw3 net6 s3 net6p vgnd nfet l=0.014u nfin=nfpf_sw
        M32 net6p vmirror_vga vgnd vgnd nfet nfin=nfpf_cm
        M31 vout_vga2 vin2 net6 vgnd nfet nfin=nfpf_dp
        M30 vout_vga1 vin1 net6 vgnd nfet nfin=nfpf_dp
        R5 vps vout_vga2 rl
        R6 vps vout_vga1 rl
        .ends {name}
    """
    )
    return netlist


def variable_gain_amplifier_ratioed(name):
    netlist = textwrap.dedent(
        f"""\
        .subckt {name} vmirror_vga s0 s1 s2 vin1 vin2 vout_vga1 vout_vga2 vps vgnd
        .param nfpf_sw=72 nfpf_sw_2=144 nfpf_sw_4=288 nfpf_cm=72 nfpf_cm_2=144 nfpf_cm_4=288 nfpf_dp=48 nfpf_dp_2=96 nfpf_dp_4=192 rl=400

        M03 vmirror_vga vmirror_vga vgnd vgnd nfet nfin=nfpf_cm m=1 nf=1
        M02 net3 vmirror_vga vgnd vgnd nfet nfin=nfpf_cm m=1  nf=1
        M01 vout_vga2 vin2 net3 vgnd nfet nfin=nfpf_dp m=1 nf=1
        M00 vout_vga1 vin1 net3 vgnd nfet nfin=nfpf_dp
        Msw0 net5 s0 net5p vgnd nfet l=0.014u nfin=nfpf_sw
        M12 net5p vmirror_vga vgnd vgnd nfet nfin=nfpf_cm
        M11 vout_vga2 vin2 net5 vgnd nfet nfin=nfpf_dp
        M10 vout_vga1 vin1 net5 vgnd nfet nfin=nfpf_dp
        Msw1 net4 s1 net4p vgnd nfet l=0.014u nfin=nfpf_sw_2
        M22 net4p vmirror_vga vgnd vgnd nfet nfin=nfpf_cm_2
        M21 vout_vga2 vin2 net4 vgnd nfet nfin=nfpf_dp_2
        M20 vout_vga1 vin1 net4 vgnd nfet nfin=nfpf_dp_2
        Msw2 net6 s2 net6p vgnd nfet l=0.014u nfin=nfpf_sw_4
        M32 net6p vmirror_vga vgnd vgnd nfet nfin=nfpf_cm_4
        M31 vout_vga2 vin2 net6 vgnd nfet nfin=nfpf_dp_4
        M30 vout_vga1 vin1 net6 vgnd nfet nfin=nfpf_dp_4
        R5 vps vout_vga2 rl
        R6 vps vout_vga1 rl
        .ends {name}
    """
    )
    return netlist


def array_limit(name):
    netlist = textwrap.dedent(
        f"""\
        .subckt {name} s
        mn1 a1 g1 s vssx n w=360e-9 nf=2 m=8
        mn2 a2 g2 s vssx n w=360e-9 nf=2 m=8
        mn3 a3 g3 s vssx n w=360e-9 nf=2 m=8
        mn4 a4 g4 s vssx n w=360e-9 nf=2 m=8
        mn5 a5 g5 s vssx n w=360e-9 nf=2 m=8
        mn6 a6 g6 s vssx n w=360e-9 nf=2 m=8
        mn7 a7 g7 s vssx n w=360e-9 nf=2 m=8
        mn8 a8 g8 s vssx n w=360e-9 nf=2 m=8
        mn9 a9 g9 s vssx n w=360e-9 nf=2 m=8
        mn10 a10 g10 s vssx n w=360e-9 nf=2 m=8
        mn11 a11 g11 s vssx n w=360e-9 nf=2 m=8
        mn12 a12 g12 s vssx n w=360e-9 nf=2 m=8
        .ends {name}
    """
    )
    return netlist


def array_mismatch(name):
    netlist = textwrap.dedent(
        f"""\
        .subckt {name} s vssx
        mn1a a1a g1a s vssx n w=360e-9 nf=2 m=8
        mn1b a1b g1b a1a vssx n w=360e-9 nf=2 m=8
        mn2a a2a g2a s vssx n w=360e-9 nf=2 m=8
        mn2b a2b g2b a2a vssx n w=360e-9 nf=2 m=8
        mn3a a3a g3a s vssx n w=360e-9 nf=2 m=8
        mn3b a3b g3b a3a vssx n w=360e-9 nf=2 m=8
        mn3c a3c g3c a3a vssx n w=360e-9 nf=2 m=8
        .ends {name}
    """
    )
    return netlist


def array_converged_net(name):
    netlist = textwrap.dedent(
        f"""\
        .subckt {name} s vssx
        mn1a a g1a s vssx n w=360e-9 nf=2 m=8
        mn1b a1b g1b a vssx n w=360e-9 nf=2 m=8
        mn2a a g2a s vssx n w=360e-9 nf=2 m=8
        mn2b a2b g2b a vssx n w=360e-9 nf=2 m=8
        mn3a a g3a s vssx n w=360e-9 nf=2 m=8
        mn3b a3b g3b a vssx n w=360e-9 nf=2 m=8
        .ends {name}
    """
    )
    return netlist


def array_converged_instance(name):
    netlist = textwrap.dedent(
        f"""\
        .subckt three_terminal a1 a2 a3
        mn1 a1 g1 s vssx n w=360e-9 nf=2 m=8
        mn2 a2 g2 s vssx n w=360e-9 nf=2 m=8
        mn3 a3 g3 s vssx n w=360e-9 nf=2 m=8
        .ends three_terminal
        .subckt {name} s vssx
        mn1 a1 g1 s vssx n w=360e-9 nf=2 m=8
        mn2 a2 g2 s vssx n w=360e-9 nf=2 m=8
        mn3 a3 g3 s vssx n w=360e-9 nf=2 m=8
        xi0 a1 a2 a3 three_terminal
        .ends {name}
    """
    )
    return netlist


def clean_data(name):
    example = my_dir / name
    if example.exists() and example.is_dir():
        shutil.rmtree(example)


def build_example(name, netlist, constraints):
    example = my_dir / name
    if example.exists() and example.is_dir():
        shutil.rmtree(example)
    example.mkdir(parents=True)
    with open(example / f"{name}.sp", "w") as fp:
        fp.write(netlist)
    if isinstance(constraints, dict):
        for k, v in constraints.items():
            with open(example / f'{k}.const.json', 'w') as fp:
                fp.write(json.dumps(v, indent=2))
    elif constraints:
        with open(example / f'{name}.const.json', 'w') as fp:
            fp.write(json.dumps(constraints, indent=2))
    return example / (name + ".sp")


def get_test_id():
    try:
        t = os.environ.get('PYTEST_CURRENT_TEST')
        t = t.split(' ')[0].split(':')[-1]
        t = t.replace('[', '_').replace(']', '').replace('-', '_')
        t = t[5:]
    except BaseException:
        t = 'debug'
    return t
