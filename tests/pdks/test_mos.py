import pathlib
import sys
import pytest


pdks = []
for prim in (pathlib.Path(__file__).parent.parent.parent / 'pdks').iterdir():
    if prim.is_dir() and (prim / 'Align_primitives.py').exists():
        pdks.append(prim)


def get_xcells_pattern(primitive, pattern, x_cells):
    # TODO: remove this name based multiplier for number of cells
    if any(primitive.startswith(f'{x}_') for x in ["CM", "CMFB"]):
        # TODO: Generalize this (pattern is ignored)
        x_cells = 2*x_cells + 2
    elif any(primitive.startswith(f'{x}_') for x in ["SCM", "CMC", "DP", "CCP", "LS"]):
        # Dual transistor primitives
        x_cells = 2*x_cells
        # TODO: Fix difficulties associated with CC patterns matching this condition
        pattern = 2 if x_cells % 4 != 0 else pattern  # CC is not possible; default is interdigitated
    return x_cells, pattern

def check_shorts(cmdlist):
    from Align_primitives import main, gen_parser
    parser = gen_parser()
    args = parser.parse_args(cmdlist)
    uc = main(args)
    assert len(uc.rd.shorts) == 0, uc.rd.shorts
    assert len(uc.rd.opens) == 0, uc.rd.opens
    assert len(uc.rd.different_widths) == 0, uc.rd.different_widths
    assert len(uc.rd.subinsts) == get_xcells_pattern(args.primitive, args.pattern, args.Xcells)[0] * args.Ycells, uc.rd.subinsts
    assert all(len(x.pins) == 4 for x in uc.rd.subinsts.values()), uc.rd.subinsts
    assert len(uc.drc.errors) == 0, uc.drc.errors


def build_test(pdk, prim, *, n, X, Y):
    sys.path.insert(0, str(pdk))
    b = f"{prim}_n{n}_X{X}_Y{Y}"
    #print(f'Testing {b} ...')
    check_shorts(['-p', prim, '-b', b, '-n', f"{n}", '-X', f"{X}", '-Y', f"{Y}"])
    sys.path.pop(0)


@pytest.mark.parametrize("pdk", pdks, ids=lambda x: x.name)
def test_mos_smoke(pdk):
    x = 2
    y = 2
    nfins = 12
    prim = 'DP_NMOS'
    build_test(pdk, prim, n=nfins, X=x, Y=y)


@pytest.mark.nightly
@pytest.mark.parametrize("y", range(1, 4), ids=lambda x: f'Y{x}')
@pytest.mark.parametrize("x", range(1, 5), ids=lambda x: f'X{x}')
@pytest.mark.parametrize("nfins", [12], ids=lambda x: f'n{x}')
@pytest.mark.parametrize("typ", ["NMOS", "PMOS"])
@pytest.mark.parametrize("pstr", [
    "{}_4T",
    "DCL_{}",
    "SCM_{}",
    "CMC_{}",
    "DP_{}"],
    ids=lambda x: x.replace('_{}', ''))
@pytest.mark.parametrize("pdk", pdks, ids=lambda x: x.name)
def test_mos_full(pdk, pstr, typ, nfins, x, y):
    prim = pstr.format(typ)
    build_test(pdk, prim, n=nfins, X=x, Y=y)

