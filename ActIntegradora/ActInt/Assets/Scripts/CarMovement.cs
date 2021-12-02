using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.AI;

public class CarMovement : MonoBehaviour
{
    public Vector3 dest;
    public int id;
    private Vector3 targetDirection;
    private Vector3 newDirection;

    void Start()
    {
        dest = Vector3.zero;
    }

    void Update() {
        if(dest != Vector3.zero){
            targetDirection = dest - transform.position;
            newDirection = Vector3.RotateTowards(transform.forward, targetDirection, Time.deltaTime*10, 0.0f);
            transform.rotation = Quaternion.LookRotation(newDirection);
            transform.position = Vector3.MoveTowards(transform.position, dest, Time.deltaTime*3);
        }
    }
}

