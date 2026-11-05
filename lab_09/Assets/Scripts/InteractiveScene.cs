using System;
using System.Collections;
using System.IO;
using UnityEngine;

namespace Lab09
{
    public class InteractiveScene : MonoBehaviour
    {
        public Material polygonMaterial, referenceMaterial, accentMaterial;
        public Camera sceneCamera;
        public Transform sculpture;
        public MeshFilter polygon;
        public LineRenderer outline;
        public Transform pivotMarker;
        public Vector3[] original;
        Matrix4x4 model = Matrix4x4.identity;
        Matrix4x4 animationBase = Matrix4x4.identity;
        Vector2 pivot = Vector2.zero;
        float angle, sx = 1.3f, sy = .7f, tx = .5f, ty = .3f, shx = .3f, shy;
        float px, py, orbit = 0;
        bool spinning;
        string last = "Ready - select a transformation";
        Mesh mesh;
        bool checking;

        void Start()
        {
            mesh = polygon.mesh;
            Refresh();
            checking = Array.IndexOf(Environment.GetCommandLineArgs(), "-lab9-check") >= 0;
            if (checking) StartCoroutine(CheckPlayer());
        }
        void Update()
        {
            sculpture.Rotate(0, 22 * Time.deltaTime, 0, Space.World);
            if (spinning)
            {
                angle = Mathf.Repeat(angle + 35 * Time.deltaTime, 360);
                model = TransformMath.PivotRotation(angle, pivot) * animationBase;
                Refresh();
            }
        }
        void Refresh()
        {
            Vector3[] points = new Vector3[original.Length];
            for (int i = 0; i < points.Length; i++) points[i] = TransformMath.Apply(model, original[i]);
            mesh.vertices = points; mesh.RecalculateNormals(); mesh.RecalculateBounds();
            outline.positionCount = points.Length - 1;
            for (int i = 0; i < points.Length - 1; i++) outline.SetPosition(i, points[i] + new Vector3(0,0,-.03f));
            pivotMarker.localPosition = new Vector3(pivot.x, pivot.y, -.08f);
        }
        public void ApplyOperation(Matrix4x4 operation, string label)
        {
            spinning = false;
            model = operation * model;
            last = label + " (world coordinates)";
            Refresh();
        }
        void ResetScene()
        {
            spinning = false; model = Matrix4x4.identity; angle = 0;
            last = "Reset to original polygon"; Refresh();
        }
        void SetPivot()
        {
            // Freeze the current animated pose before changing the pivot.
            spinning = false; pivot = new Vector2(px, py); Refresh();
        }
        void OnGUI()
        {
            float scale = Mathf.Min(Screen.width / 1280f, Screen.height / 800f);
            GUI.matrix = Matrix4x4.Scale(new Vector3(scale, scale, 1));
            GUILayout.BeginArea(new Rect(18, 18, 340, 762), GUI.skin.box);
            GUILayout.Label("EXPERIMENT 09  |  UNITY", Title());
            GUILayout.Label("Interactive transformation studio", SubTitle());
            GUILayout.Space(8);
            GUILayout.Label("Teal: transformed polygon\nGold: original outline  |  Pink: pivot\nGrid: one world unit per square");
            GUILayout.Space(6);
            tx = Slider("Translate X", tx, -2, 2); ty = Slider("Translate Y", ty, -2, 2);
            if (GUILayout.Button("Translate")) ApplyOperation(TransformMath.Translation(tx, ty), "Translation");
            px = Slider("Pivot X", px, -2, 2); py = Slider("Pivot Y", py, -2, 2);
            GUILayout.BeginHorizontal();
            if (GUILayout.Button("Set pivot")) SetPivot();
            if (GUILayout.Button("Rotate +30 degrees")) { SetPivot(); ApplyOperation(TransformMath.PivotRotation(30, pivot), "Pivot rotation"); }
            GUILayout.EndHorizontal();
            sx = Slider("Scale X", sx, .2f, 2); sy = Slider("Scale Y", sy, .2f, 2);
            if (GUILayout.Button("Non-uniform scale")) ApplyOperation(TransformMath.Scale(sx, sy), "Non-uniform scale");
            if (GUILayout.Button("Reflect across y = x")) ApplyOperation(TransformMath.Reflection(), "Reflection in y=x");
            shx = Slider("Shear X", shx, -.8f, .8f); shy = Slider("Shear Y", shy, -.8f, .8f);
            if (GUILayout.Button("Shear")) ApplyOperation(TransformMath.Shear(shx, shy), "Shear");
            if (GUILayout.Button("Composite: scale, rotate, translate"))
                ApplyOperation(TransformMath.Translation(tx, ty) * TransformMath.PivotRotation(30, pivot) * TransformMath.Scale(sx, sy), "T * R(pivot) * S");
            GUILayout.BeginHorizontal();
            if (GUILayout.Button(spinning ? "Pause rotation" : "Animate rotation"))
            {
                spinning = !spinning; animationBase = model; angle = 0;
            }
            if (GUILayout.Button("Reset polygon")) ResetScene();
            GUILayout.EndHorizontal();
            orbit = Slider("Camera orbit", orbit, -28, 28);
            sceneCamera.transform.position = new Vector3(orbit / 9, 1.5f, -14);
            sceneCamera.transform.LookAt(new Vector3(1.1f, .2f, 0));
            GUILayout.Label(last);
            GUILayout.Label("Column vectors: p' = M p\nNew operations multiply on the left.");
            GUILayout.Label(string.Format("Current 4 x 4 matrix\n{0,6:F2} {1,6:F2} {2,6:F2} {3,6:F2}\n{4,6:F2} {5,6:F2} {6,6:F2} {7,6:F2}\n{8,6:F2} {9,6:F2} {10,6:F2} {11,6:F2}\n{12,6:F2} {13,6:F2} {14,6:F2} {15,6:F2}",
                model.m00,model.m01,model.m02,model.m03,model.m10,model.m11,model.m12,model.m13,
                model.m20,model.m21,model.m22,model.m23,model.m30,model.m31,model.m32,model.m33));
            GUILayout.EndArea();
            GUI.Label(new Rect(860, 35, 400, 90), "3D SCENE\nLit geometry / depth / perspective", SubTitle());
        }
        static GUIStyle Title() => new GUIStyle(GUI.skin.label) { fontSize = 20, fontStyle = FontStyle.Bold };
        static GUIStyle SubTitle() => new GUIStyle(GUI.skin.label) { fontSize = 16 };
        static float Slider(string label, float value, float min, float max)
        {
            GUILayout.BeginHorizontal(); GUILayout.Label(label + " " + value.ToString("F2"), GUILayout.Width(150));
            value = GUILayout.HorizontalSlider(value, min, max); GUILayout.EndHorizontal(); return value;
        }
        static void Require(bool condition, string message)
        {
            if (!condition) throw new Exception(message);
        }
        IEnumerator CheckPlayer()
        {
            yield return null;
            string directory = Path.GetFullPath(Path.Combine(Application.dataPath, "../../outputs"));
            Directory.CreateDirectory(directory);
            string result;
            try
            {
                Vector3 p = new Vector3(2, 1, 0);
                Require(Vector3.Distance(TransformMath.Apply(TransformMath.PivotRotation(90, new Vector2(1,1)), p), new Vector3(1,2,0)) < .0001f, "Pivot rotation");
                Require(TransformMath.Apply(TransformMath.Scale(2,3), p) == new Vector3(4,3,0), "Scale");
                Require(TransformMath.Apply(TransformMath.Reflection(), p) == new Vector3(1,2,0), "Reflection");
                Require(TransformMath.Apply(TransformMath.Shear(.5f,0), p) == new Vector3(2.5f,1,0), "Shear");
                ApplyOperation(TransformMath.Translation(1,0), "Runtime check");
                Require(Vector3.Distance(mesh.vertices[1], original[1] + Vector3.right) < .0001f, "Runtime mesh update");
                ResetScene();
                Require(Vector3.Distance(mesh.vertices[1], original[1]) < .0001f, "Reset");
                result = "PASS: player startup, pivot rotation, non-uniform scale, reflection, shear, runtime mesh update, reset.\n";
            }
            catch (Exception ex) { result = "FAIL: " + ex; }
            File.WriteAllText(Path.Combine(directory, "player-check.txt"), result + "Unity " + Application.unityVersion + "\n" + SystemInfo.graphicsDeviceName);
            yield return new WaitForEndOfFrame();
            ScreenCapture.CaptureScreenshot(Path.Combine(directory, "interactive-scene.png"));
            yield return new WaitForSeconds(2);
            ApplyOperation(TransformMath.Translation(.5f,.3f) * TransformMath.PivotRotation(30, new Vector2(1,1)) * TransformMath.Scale(1.3f,.7f), "Composite demonstration");
            pivot = new Vector2(1,1); px = py = 1; Refresh();
            yield return new WaitForEndOfFrame();
            ScreenCapture.CaptureScreenshot(Path.Combine(directory, "composite-scene.png"));
            Vector3 before = mesh.vertices[1]; Quaternion cubeBefore = sculpture.rotation;
            animationBase = model; angle = 0; spinning = true;
            yield return new WaitForSeconds(1);
            bool animated = Vector3.Distance(before, mesh.vertices[1]) > .01f && Quaternion.Angle(cubeBefore, sculpture.rotation) > 1;
            File.AppendAllText(Path.Combine(directory, "player-check.txt"), "\n" + (animated ? "PASS" : "FAIL") + ": polygon and 3D cube time-based animation\n");
            if (!animated) result = "FAIL: animation";
            spinning = false;
            yield return new WaitForEndOfFrame();
            ScreenCapture.CaptureScreenshot(Path.Combine(directory, "animated-scene.png"));
            yield return new WaitForSeconds(1);
            Application.Quit(result.StartsWith("PASS") ? 0 : 1);
        }
    }
}
