using UnityEngine;

namespace Lab09
{
    // Column vectors: Apply(A * B, p) applies B first, then A.
    public static class TransformMath
    {
        public static Vector3 Apply(Matrix4x4 matrix, Vector3 point)
        {
            Vector4 p = matrix * new Vector4(point.x, point.y, point.z, 1);
            return new Vector3(p.x, p.y, p.z) / p.w;
        }
        public static Matrix4x4 Translation(float x, float y) => Matrix4x4.Translate(new Vector3(x, y, 0));
        public static Matrix4x4 Scale(float x, float y) => Matrix4x4.Scale(new Vector3(x, y, 1));
        public static Matrix4x4 Rotation(float degrees) => Matrix4x4.Rotate(Quaternion.AngleAxis(degrees, Vector3.forward));
        public static Matrix4x4 PivotRotation(float degrees, Vector2 pivot) =>
            Translation(pivot.x, pivot.y) * Rotation(degrees) * Translation(-pivot.x, -pivot.y);
        public static Matrix4x4 Reflection()
        {
            Matrix4x4 m = Matrix4x4.identity;
            m.m00 = m.m11 = 0; m.m01 = m.m10 = 1; return m;
        }
        public static Matrix4x4 Shear(float x, float y)
        {
            Matrix4x4 m = Matrix4x4.identity; m.m01 = x; m.m10 = y; return m;
        }
    }
}
