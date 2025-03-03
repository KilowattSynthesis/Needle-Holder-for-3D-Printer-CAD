from dataclasses import dataclass
from pathlib import Path

import build123d as bd
import build123d_ease as bde
from build123d_ease import show
from loguru import logger


@dataclass
class Spec:
    """Specification for bearing_holder."""

    bearing_od: float = 16
    bearing_id: float = 8.0 - 0.1
    bearing_thickness: float = 5.0

    gap_between_bearings = 2.0

    general_wall_thickness: float = 3.0

    needle_shaft_length: float = 16.0
    needle_shaft_od: float = 2.0 + 0.25
    needle_shaft_flats_width: float = 1.5 + 0.2

    mount_stepper_width: float = 42.0
    mount_stepper_interface_depth: float = 20
    mount_stepper_top_to_bottom_bearing_bottom: float = 94.0
    dist_stepper_to_needle_axis: float = 32.0

    raiser_width_x: float = 15.0
    raiser_width_y: float = 10.0

    def __post_init__(self) -> None:
        """Post initialization checks."""

    @property
    def bearing_holder_z_height(self) -> float:
        """Height of the bearing holder."""
        return self.bearing_thickness * 2 + self.gap_between_bearings


def stepper_grip(spec: Spec) -> bd.Part | bd.Compound:
    """Create a CAD model of bearing_holder."""
    p = bd.Part(None)

    # Add the stepper motor mount.
    p += bd.Pos(
        Y=spec.dist_stepper_to_needle_axis,
        Z=(spec.mount_stepper_top_to_bottom_bearing_bottom),
    ) * bd.Box(
        spec.mount_stepper_width + 2 * spec.general_wall_thickness,
        spec.mount_stepper_interface_depth + spec.general_wall_thickness,
        spec.mount_stepper_width + spec.general_wall_thickness,
        align=(bd.Align.CENTER, bd.Align.MIN, bd.Align.MAX),
    )

    # Add extension out to the bearing holder.
    p += bd.Pos(
        Y=spec.bearing_od / 2,
        Z=(spec.mount_stepper_top_to_bottom_bearing_bottom),
    ) * bd.Box(
        spec.mount_stepper_width / 2,
        spec.dist_stepper_to_needle_axis,
        spec.mount_stepper_width + spec.general_wall_thickness,
        align=(bd.Align.CENTER, bd.Align.MIN, bd.Align.MAX),
    )

    # Remove the literal stepper motor.
    p -= bd.Pos(
        Y=spec.dist_stepper_to_needle_axis + spec.general_wall_thickness,
        Z=(
            spec.mount_stepper_top_to_bottom_bearing_bottom
            - spec.general_wall_thickness
        ),
    ) * bd.Box(
        spec.mount_stepper_width,
        spec.mount_stepper_interface_depth,
        spec.mount_stepper_width,
        align=(bd.Align.CENTER, bd.Align.MIN, bd.Align.MAX),
    )

    # Remove the raiser rod.
    p -= bd.Pos(
        Y=spec.bearing_od / 2,
    ) * bd.Box(
        spec.raiser_width_x + 0.1,
        spec.raiser_width_y + 0.1,
        spec.mount_stepper_top_to_bottom_bearing_bottom * 2,
        align=(bd.Align.CENTER, bd.Align.MIN, bd.Align.MIN),
    )

    # Remove bolts.
    for z in (-8, -21, -34):
        p -= bd.Pos(
            Y=spec.bearing_od / 2 + spec.raiser_width_y / 2,
            Z=(spec.mount_stepper_top_to_bottom_bearing_bottom + z),
        ) * bd.Cylinder(
            radius=3.2 / 2,
            height=spec.mount_stepper_width * 2,
            rotation=bde.rotation.POS_X,
        )

    return p


def bearing_holder(spec: Spec) -> bd.Part | bd.Compound:
    """Create a CAD model of bearing_holder and vertical bar."""
    p = bd.Part(None)

    # Draw the bearing holder.
    p += bd.Cylinder(
        radius=(spec.bearing_od / 2 + spec.general_wall_thickness),
        height=(spec.bearing_thickness * 2 + spec.gap_between_bearings),
        align=bde.align.ANCHOR_BOTTOM,
    )

    # From the bearing holder, draw funky members up to the stepper motor part.
    # p += bd.Box(
    #     raiser_width_x,
    #     spec.bearing_od / 2 + 10,
    #     spec.bearing_holder_z_height,
    #     align=(bd.Align.CENTER, bd.Align.MIN, bd.Align.MIN),
    # )
    p += bd.Pos(Y=spec.bearing_od / 2 + spec.raiser_width_y) * bd.Box(
        spec.raiser_width_x,
        spec.raiser_width_y,
        spec.mount_stepper_top_to_bottom_bearing_bottom,
        align=(bd.Align.CENTER, bd.Align.MAX, bd.Align.MIN),
    )

    # Remove each of the bearings.
    for bottom_z in (0, spec.bearing_thickness + spec.gap_between_bearings):
        p -= bd.Pos(Z=bottom_z) * bd.Cylinder(
            radius=spec.bearing_od / 2,
            height=spec.bearing_thickness,
            align=bde.align.ANCHOR_BOTTOM,
        )

    # Remove hole though the middle.
    p -= bd.Cylinder(
        radius=(spec.bearing_od - 4) / 2,
        height=(spec.bearing_thickness * 2 + spec.gap_between_bearings),
        align=bde.align.ANCHOR_BOTTOM,
    )

    # Make it easier to pop the bearings out.
    p -= bd.Pos(
        Y=-spec.bearing_od / 2 - 1,
        Z=spec.bearing_holder_z_height / 2,
    ) * bd.Box(5, spec.bearing_od / 2, spec.gap_between_bearings + 3)

    # Remove bolts.
    for z in (-8, -21, -34):
        p -= bd.Pos(
            Y=spec.bearing_od / 2 + spec.raiser_width_y / 2,
            Z=(spec.mount_stepper_top_to_bottom_bearing_bottom + z),
        ) * bd.Cylinder(
            radius=3.2 / 2,
            height=spec.mount_stepper_width * 2,
            rotation=bde.rotation.POS_X,
        )

    return p


def assembly(spec: Spec) -> bd.Part | bd.Compound:
    """Create a CAD model of the assembly."""
    p = bd.Part(None)

    # Add the bearing holder.
    p += bearing_holder(spec)

    # Add the stepper motor mount.
    p += stepper_grip(spec)

    p += bd.Pos(X=25) * bearing_adapter(spec)

    return p


def bearing_adapter(spec: Spec) -> bd.Part | bd.Compound:
    """Adapter on the inside of the bearing, to the sewing needle."""
    p = bd.Part(None)

    p += bd.Cylinder(
        radius=spec.bearing_id / 2,
        height=spec.bearing_holder_z_height,
        align=bde.align.ANCHOR_BOTTOM,
    )

    # Add flange.
    p += bd.Cylinder(
        radius=spec.bearing_id / 2 + 2,
        height=spec.general_wall_thickness,
        align=bde.align.ANCHOR_TOP,
    )

    # Remove the needle shaft (round, with flats).
    p -= bd.Cylinder(
        radius=spec.needle_shaft_od / 2,
        height=spec.bearing_holder_z_height,
        align=bde.align.ANCHOR_BOTTOM,
    ) & bd.Box(
        spec.needle_shaft_flats_width,
        10,
        spec.bearing_holder_z_height,
        align=bde.align.ANCHOR_BOTTOM,
    )

    return p


if __name__ == "__main__":
    parts = {
        "assembly": show(assembly(Spec())),
        "bearing_holder": (bearing_holder(Spec())),
        "stepper_grip": (stepper_grip(Spec())),
        "bearing_adapter": (bearing_adapter(Spec())),
    }

    logger.info("Showing CAD model(s)")

    (export_folder := Path(__file__).parent.with_name("build")).mkdir(
        exist_ok=True
    )
    for name, part in parts.items():
        assert isinstance(part, bd.Part | bd.Solid | bd.Compound), (
            f"{name} is not an expected type ({type(part)})"
        )
        if not part.is_manifold:
            logger.warning(f"Part '{name}' is not manifold")

        bd.export_stl(part, str(export_folder / f"{name}.stl"))
        bd.export_step(part, str(export_folder / f"{name}.step"))
