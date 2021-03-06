import pytest
import numpy as np
from pytest import approx
import matplotlib.pyplot
import matplotlib.lines
import mplhep as hep
import copy
from types import SimpleNamespace


@pytest.fixture
def mock_matplotlib(mocker):
    fig = mocker.Mock(spec=matplotlib.pyplot.Figure)
    ax = mocker.Mock(spec=matplotlib.pyplot.Axes)
    line2d = mocker.Mock(name="step", spec=matplotlib.lines.Line2D)
    line2d.get_color.return_value = "current-color"
    ax.step.return_value = (line2d,)
    ax.plot.return_value = (line2d,)

    mpl = mocker.patch("matplotlib.pyplot", autospec=True)
    mocker.patch("matplotlib.pyplot.subplots", return_value=(fig, ax))

    return SimpleNamespace(fig=fig, ax=ax, line2d=line2d, mpl=mpl)


def test_simple(mock_matplotlib):
    ax = mock_matplotlib.ax

    h = [1, 3, 2]
    bins = [0, 1, 2, 3]
    hep.histplot(h, bins, yerr=True, label="X", ax=ax)

    assert len(ax.mock_calls) == 3

    ax.step.assert_called_once_with(
        approx([0.0, 0.0, 1.0, 2.0, 3.0, 3.0]),
        approx([0, 1.0, 3.0, 2.0, 2.0, 0]),
        where="post",
        label=None,
        marker="",
    )

    assert ax.errorbar.call_count == 2
    ax.errorbar.assert_any_call(
        approx([]), approx([]), yerr=1, xerr=1, color="current-color", label="X"
    )
    ax.errorbar.assert_any_call(
        approx([0.5, 1.5, 2.5]),
        approx([1, 3, 2]),
        yerr=[
            approx([1.0, 1.73205081, 1.41421356]),
            approx([1.0, 1.73205081, 1.41421356]),
        ],
        color="current-color",
        linestyle="none",
    )


def test_histplot_real(mock_matplotlib):
    np.random.seed(0)
    h, bins = np.histogram(np.random.normal(10, 3, 1000), bins=10)

    ax = mock_matplotlib.ax
    a, b, c = h, h * 2, np.random.poisson(h * 3)

    hep.histplot([a, b, c], bins=bins, ax=ax, yerr=True, label=["MC1", "MC2", "Data"])
    ax.legend()
    ax.set_title("Raw")
    assert len(ax.mock_calls) == 11

    ax.reset_mock()

    hep.histplot([a, b], bins=bins, ax=ax, stack=True, label=["MC1", "MC2"])
    hep.histplot([c], bins=bins, ax=ax, yerr=True, histtype="errorbar", label="Data")
    ax.legend()
    ax.set_title("Data/MC")
    assert len(ax.mock_calls) == 6
    ax.reset_mock()

    hep.histplot(
        [a, b], bins=bins, ax=ax, stack=True, label=["MC1", "MC2"], binwnorm=[2, 1]
    )
    hep.histplot(
        c,
        bins=bins,
        ax=ax,
        yerr=True,
        histtype="errorbar",
        label="Data",
        binwnorm=1,
    )
    ax.legend()
    ax.set_title("Data/MC binwnorm")
    assert len(ax.mock_calls) == 6
    ax.reset_mock()

    hep.histplot(
        [a, b], bins=bins, ax=ax, stack=True, label=["MC1", "MC2"], density=True
    )
    hep.histplot(
        c,
        bins=bins,
        ax=ax,
        yerr=True,
        histtype="errorbar",
        label="Data",
        density=True,
    )
    ax.legend()
    ax.set_title("Data/MC Density")
    assert len(ax.mock_calls) == 6
