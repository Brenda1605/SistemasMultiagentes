using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class WheelMove : MonoBehaviour
{
    [SerializeField] GameObject wheel1;
    [SerializeField] GameObject wheel2;
    [SerializeField] GameObject wheel3;
    [SerializeField] GameObject wheel4;
    public Vector3 vector;

    float i = 0;
    // Start is called before the first frame update
    void Start()
    {
        vector = Vector3.zero;
    }

    // Update is called once per frame
    void Update()
    {
       
        wheel1.transform.Rotate(0, 0, -1f);
        wheel2.transform.Rotate(0, 0, -1f);
        wheel3.transform.Rotate(0, 0, 1f);
        wheel4.transform.Rotate(0, 0, 1f);

        

    }

}
