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

    spool_width: float = 14.0
    spool_diameter: float = 72.0

    def __post_init__(self) -> None:
        """Post initialization checks."""

    @property
    def bearing_holder_z_height(self) -> float:
        """Height of the bearing holder."""
        return self.bearing_thickness * 2 + self.gap_between_bearings

    @property
    def diameter_at_spool_holder(self) -> float:
        """Mating diameter at the the rotating rod riser and the spool holder.

        Also the diameter of the long part of the bearing adapter.
        """
        return self.bearing_id - 0.7


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

    # Draw the bearing holder (bottom).
    p += bd.Cylinder(
        radius=(spec.bearing_od / 2 + spec.general_wall_thickness),
        height=(spec.bearing_thickness * 2 + spec.gap_between_bearings),
        align=bde.align.ANCHOR_BOTTOM,
    )

    # Remove each of the bearings (bottom).
    for bottom_z in (0, spec.bearing_thickness + spec.gap_between_bearings):
        p -= bd.Pos(Z=bottom_z) * bd.Cylinder(
            radius=spec.bearing_od / 2,
            height=spec.bearing_thickness,
            align=bde.align.ANCHOR_BOTTOM,
        )

    # Draw the bearing holder (top).
    p += bd.Pos(Z=spec.mount_stepper_top_to_bottom_bearing_bottom) * (
        bd.Cylinder(
            radius=(spec.bearing_od / 2 + spec.general_wall_thickness),
            height=(spec.bearing_thickness),
            align=bde.align.ANCHOR_TOP,
        )
        - bd.Cylinder(
            radius=(spec.bearing_od / 2),
            height=(spec.bearing_thickness),
            align=bde.align.ANCHOR_TOP,
        )
    )

    # Draw the raiser rod.
    p += bd.Pos(Y=spec.bearing_od / 2 + spec.raiser_width_y) * bd.Box(
        spec.raiser_width_x,
        spec.raiser_width_y,
        spec.mount_stepper_top_to_bottom_bearing_bottom,
        align=(bd.Align.CENTER, bd.Align.MAX, bd.Align.MIN),
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

    p += bd.Pos(
        X=50, Z=spec.mount_stepper_top_to_bottom_bearing_bottom
    ) * spool_holder(spec)

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
    p += bd.Pos(Z=spec.bearing_holder_z_height) * bd.Cone(
        top_radius=8 / 2,
        bottom_radius=spec.bearing_id / 2 + 2,
        height=spec.general_wall_thickness,
        align=bde.align.ANCHOR_BOTTOM,
    )

    # Add part all the way to the top.
    p += bd.Pos(Z=0) * bd.Cylinder(
        radius=spec.diameter_at_spool_holder / 2,
        height=spec.mount_stepper_top_to_bottom_bearing_bottom + 12,
        align=bde.align.ANCHOR_BOTTOM,
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

    # Remove passage for the thread/wire (bottom).
    p -= bd.Pos(Z=spec.bearing_holder_z_height + 2) * bd.Cylinder(
        radius=3.2 / 2,
        height=spec.bearing_holder_z_height * 5,
    ).rotate(axis=bd.Axis.Y, angle=40)

    # Remove passage for the thread/wire (top, on +X side).
    p -= bd.Pos(
        X=spec.bearing_id / 2,
        Z=spec.mount_stepper_top_to_bottom_bearing_bottom,
    ) * bd.Box(
        3,
        3,
        25,
        align=(bd.Align.MAX, bd.Align.CENTER, bd.Align.CENTER),
    )

    # Remove M3 hole in the top.
    p -= bd.Pos(
        Z=spec.mount_stepper_top_to_bottom_bearing_bottom + 7,
    ) * bd.Cylinder(
        radius=2.8 / 2,
        height=40,
        rotation=bde.rotation.POS_Y,
    )

    return p


def spool_holder(spec: Spec) -> bd.Part | bd.Compound:
    """Make the spool holder."""
    p = bd.Part(None)

    base_t = 10

    p += bd.Box(
        spec.spool_width + 2 * spec.general_wall_thickness,
        10,
        base_t + spec.spool_diameter / 2 + 10,
        align=bde.align.ANCHOR_BOTTOM,
    )

    p -= bd.Cylinder(
        radius=spec.diameter_at_spool_holder / 2 + 0.25,
        height=10,
        align=bde.align.ANCHOR_BOTTOM,
    )

    # Remove screw hole.
    p -= bd.Pos(Z=10 / 2) * bd.Cylinder(
        radius=3.2 / 2,
        height=100,
        rotation=bde.rotation.POS_X,
    )

    # Remove the spool.
    p -= bd.Pos(Z=base_t) * bd.Box(
        spec.spool_width,
        100,
        1000,
        align=bde.align.ANCHOR_BOTTOM,
    )

    # Remove the screw through the spool.
    p -= bd.Pos(Z=base_t + spec.spool_diameter / 2) * bd.Cylinder(
        radius=3.2 / 2,
        height=1000,
        rotation=bde.rotation.POS_X,
    )

    return p


if __name__ == "__main__":
    parts = {
        "assembly": show(assembly(Spec())),
        "bearing_holder": (bearing_holder(Spec())),
        "stepper_grip": (stepper_grip(Spec())),
        "bearing_adapter": (bearing_adapter(Spec())),
        "spool_holder": (spool_holder(Spec())),
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
