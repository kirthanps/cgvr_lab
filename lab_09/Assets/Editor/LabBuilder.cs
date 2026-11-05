using System;
using System.IO;
using Lab09;
using UnityEditor;
using UnityEditor.Build;
using UnityEditor.Build.Reporting;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;

public static class LabBuilder
{
    static Material Material(string name, Color color, bool lit = false)
    {
        var m = new Material(Shader.Find(lit ? "Standard" : "Lab09/TwoSidedColor")); m.color = color;
        AssetDatabase.CreateAsset(m, "Assets/Materials/" + name + ".mat"); return m;
    }
    static LineRenderer Line(string name, Vector3[] points, Material mat, float width, bool loop = false)
    {
        var line = new GameObject(name).AddComponent<LineRenderer>();
        line.useWorldSpace = false; line.positionCount = points.Length; line.SetPositions(points);
        line.sharedMaterial = mat; line.startWidth = line.endWidth = width; line.loop = loop; return line;
    }
    [MenuItem("Lab 09/Create scene and build Windows player")]
    public static void Build()
    {
        Directory.CreateDirectory("Assets/Scenes"); Directory.CreateDirectory("Assets/Materials");
        Directory.CreateDirectory("Assets/Meshes"); Directory.CreateDirectory("outputs");
        EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
        var teal = Material("Teal", new Color(.04f,.74f,.69f));
        var gold = Material("Gold", new Color(1,.72f,.25f));
        var pink = Material("Pink", new Color(1,.25f,.55f));
        var grid = Material("Grid", new Color(.13f,.21f,.29f));
        var blue = Material("Blue sculpture", new Color(.15f,.45f,.95f), true);
        var floor = Material("Stage", new Color(.065f,.095f,.14f), true);
        var camera = new GameObject("Main Camera").AddComponent<Camera>(); camera.tag = "MainCamera";
        camera.transform.position = new Vector3(0,1.5f,-14); camera.transform.LookAt(new Vector3(1.1f,.2f,0));
        camera.clearFlags = CameraClearFlags.SolidColor; camera.backgroundColor = new Color(.025f,.045f,.075f);
        camera.fieldOfView = 42; camera.nearClipPlane = .1f; camera.farClipPlane = 100;
        var light = new GameObject("Directional Light").AddComponent<Light>(); light.type = LightType.Directional;
        light.intensity = 1.3f; light.transform.rotation = Quaternion.Euler(35,-30,0);
        RenderSettings.ambientLight = new Color(.5f,.5f,.6f);
        for (int i = -5; i <= 5; i++)
        {
            Line("Grid vertical " + i, new[]{new Vector3(i,-4,.12f),new Vector3(i,4,.12f)}, grid, .012f);
            Line("Grid horizontal " + i, new[]{new Vector3(-5,i,.12f),new Vector3(5,i,.12f)}, grid, .012f);
        }
        Line("X axis", new[]{new Vector3(-5,0,.1f),new Vector3(5,0,.1f)}, gold,.025f);
        Line("Y axis", new[]{new Vector3(0,-4,.1f),new Vector3(0,4,.1f)}, gold,.025f);
        Line("Reflection line y=x", new[]{new Vector3(-4,-4,.08f),new Vector3(4,4,.08f)}, pink,.015f);
        var original = new Vector3[11];
        for (int i=0;i<10;i++)
        {
            float a = (90+i*36)*Mathf.Deg2Rad; float r = i%2==0 ? 1.7f : .82f;
            original[i] = new Vector3(Mathf.Cos(a)*r,Mathf.Sin(a)*r,0);
        }
        var mesh = new Mesh { name = "Concave star polygon" }; mesh.vertices = original;
        int[] triangles = new int[30];
        for(int i=0;i<10;i++) { triangles[i*3]=10; triangles[i*3+1]=(i+1)%10; triangles[i*3+2]=i; }
        mesh.triangles=triangles; mesh.RecalculateNormals(); mesh.RecalculateBounds();
        AssetDatabase.CreateAsset(mesh,"Assets/Meshes/Star.asset");
        var obj = new GameObject("Transformed polygon",typeof(MeshFilter),typeof(MeshRenderer));
        obj.GetComponent<MeshFilter>().sharedMesh=mesh; obj.GetComponent<MeshRenderer>().sharedMaterial=teal;
        var outline = Line("Transformed outline",new Vector3[10],teal,.035f,true);
        var refPoints = new Vector3[10];
        for(int i=0;i<10;i++) refPoints[i]=original[i]+new Vector3(0,0,-.06f);
        Line("Original polygon reference",refPoints,gold,.035f,true);
        var marker=GameObject.CreatePrimitive(PrimitiveType.Sphere); marker.name="Pivot marker";
        marker.transform.localScale=Vector3.one*.12f; marker.GetComponent<Renderer>().sharedMaterial=pink;
        var sculpture=GameObject.CreatePrimitive(PrimitiveType.Cube); sculpture.name="Animated 3D cube";
        sculpture.transform.position=new Vector3(4,-.25f,0); sculpture.transform.localScale=new Vector3(1.25f,1.8f,1.25f);
        sculpture.transform.rotation=Quaternion.Euler(15,25,10); sculpture.GetComponent<Renderer>().sharedMaterial=blue;
        var stage=GameObject.CreatePrimitive(PrimitiveType.Cube); stage.name="3D stage";
        stage.transform.position=new Vector3(3.8f,-1.5f,.4f); stage.transform.localScale=new Vector3(3,.2f,3);
        stage.GetComponent<Renderer>().sharedMaterial=floor;
        var demo=new GameObject("Lab 09 Controller").AddComponent<InteractiveScene>();
        demo.original=original; demo.polygon=obj.GetComponent<MeshFilter>(); demo.outline=outline;
        demo.pivotMarker=marker.transform; demo.sceneCamera=camera; demo.sculpture=sculpture.transform;
        demo.polygonMaterial=teal; demo.referenceMaterial=gold; demo.accentMaterial=pink;
        const string scene="Assets/Scenes/InteractiveScene.unity";
        EditorSceneManager.SaveScene(UnityEngine.SceneManagement.SceneManager.GetActiveScene(),scene);
        EditorBuildSettings.scenes=new[]{new EditorBuildSettingsScene(scene,true)};
        PlayerSettings.companyName="CGVR Lab"; PlayerSettings.productName="Lab 09 - Transformation Studio";
        PlayerSettings.defaultScreenWidth=1280; PlayerSettings.defaultScreenHeight=800;
        PlayerSettings.fullScreenMode=FullScreenMode.Windowed;
        PlayerSettings.runInBackground=true;
        PlayerSettings.SetScriptingBackend(NamedBuildTarget.Standalone,ScriptingImplementation.Mono2x);
        PlayerSettings.SetUseDefaultGraphicsAPIs(BuildTarget.StandaloneWindows64,false);
        PlayerSettings.SetGraphicsAPIs(BuildTarget.StandaloneWindows64,new[]{GraphicsDeviceType.Direct3D11});
        AssetDatabase.SaveAssets();
        Validate();
        var report=BuildPipeline.BuildPlayer(new BuildPlayerOptions { scenes=new[]{scene}, locationPathName="Build/Lab09.exe", target=BuildTarget.StandaloneWindows64, options=BuildOptions.None });
        File.WriteAllText("outputs/build-result.txt", "Unity " + Application.unityVersion + "\n" + report.summary.result + "\nErrors: " + report.summary.totalErrors + "\nWarnings: " + report.summary.totalWarnings);
        if(report.summary.result!=BuildResult.Succeeded) throw new Exception("Lab 09 build failed");
    }
    static void Validate()
    {
        int count=0;
        Action<Vector3,Vector3> equal=(actual,expected)=> { if(Vector3.Distance(actual,expected)>.0001f) throw new Exception("Matrix check failed: "+actual+" expected "+expected); count++; };
        var p=new Vector3(2,1,0);
        equal(TransformMath.Apply(TransformMath.Translation(3,-2),p),new Vector3(5,-1,0));
        equal(TransformMath.Apply(TransformMath.PivotRotation(90,new Vector2(1,1)),p),new Vector3(1,2,0));
        equal(TransformMath.Apply(TransformMath.PivotRotation(73,new Vector2(2,1)),p),p);
        equal(TransformMath.Apply(TransformMath.Scale(2,3),p),new Vector3(4,3,0));
        equal(TransformMath.Apply(TransformMath.Reflection(),p),new Vector3(1,2,0));
        equal(TransformMath.Apply(TransformMath.Reflection()*TransformMath.Reflection(),p),p);
        equal(TransformMath.Apply(TransformMath.Shear(.5f,.25f),p),new Vector3(2.5f,1.5f,0));
        var t=TransformMath.Translation(1,2); var r=TransformMath.Rotation(90); var s=TransformMath.Scale(2,3);
        equal(TransformMath.Apply(t*r*s,p),TransformMath.Apply(t,TransformMath.Apply(r,TransformMath.Apply(s,p))));
        equal(TransformMath.Apply(t*s,p),new Vector3(5,5,0));
        equal(TransformMath.Apply(s*t,p),new Vector3(6,9,0));
        File.WriteAllText("outputs/matrix-checks.txt","PASS: "+count+" independent known-value / composition checks in Unity "+Application.unityVersion);
    }
}
