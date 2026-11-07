"""Course-map placeholders are metadata only; kinematics is the sole built level."""
LEVELS = [
    ('kinematics', 'Kinematics', 'Position, velocity, acceleration. Learn to read motion.', '01', '↗', 'available'),
    ('dynamics', 'Forces & energy', 'Newton’s laws, constraints, work and conservation.', '02', '⚡', 'planned'),
    ('oscillations', 'Oscillations', 'Harmonic motion, damping and resonance.', '03', '∿', 'planned'),
    ('momentum', 'Momentum & collisions', 'Systems, impulse and changing motion.', '04', '⇄', 'planned'),
    ('gravitation', 'Gravitation', 'Orbits, fields and gravitational potential.', '05', '◎', 'planned'),
    ('rigid-body', 'Rigid bodies', 'Rotation, rolling and mechanical equilibrium.', '06', '⟳', 'planned'),
    ('fluids', 'Fluids', 'Pressure, flow and ideal-fluid models.', '07', '≈', 'source_gap'),
    ('thermodynamics', 'Thermodynamics', 'Temperature, heat and the first law.', '08', '♨', 'planned'),
    ('entropy', 'Cycles & entropy', 'Heat engines, the second law and entropy.', '09', '∞', 'planned'),
]


def course_catalogue():
    return {'id': 'physics-1', 'title': 'Physics I', 'subtitle': 'Mechanics & thermodynamics',
            'levels': [dict(zip(('id','title','description','number','icon','status'), row)) for row in LEVELS],
            'note': 'Only Kinematics is built. Other cards show the proposed course map, not published lessons.'}
