using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Networking;
using System;

public class Requesting : MonoBehaviour
{
    [SerializeField] private GameObject carPrefab;
    [SerializeField] private GameObject carGroup;
    [SerializeField] private GameObject [] trafficLights = new GameObject[2];
    private CarMovement carMovement;
    private Data d;
    private GameObject newCar;
    private HashSet<int> existingCars = new HashSet<int>();

    void Start() {
        StartCoroutine(Wait());
    }

    
    void UpdateTrafficLights(){
        int i = 0;
        foreach(Semaforo s in d.trafficLights){
            if(s.color == "GREEN"){
                GreenLight(i);
            } else if (s.color == "YELLOW"){
                YellowLight(i);
            }else{
                RedLight(i);
            }
            i++;
        }
    }

    void GreenLight(int i){
        trafficLights[i].transform.Find("GREEN").GetComponent<Light>().intensity = 2;
        trafficLights[i].transform.Find("YELLOW").GetComponent<Light>().intensity = 0;
        trafficLights[i].transform.Find("RED").GetComponent<Light>().intensity = 0;
    }

    void YellowLight(int i){
        trafficLights[i].transform.Find("YELLOW").GetComponent<Light>().intensity = 2;
        trafficLights[i].transform.Find("GREEN").GetComponent<Light>().intensity = 0;
        trafficLights[i].transform.Find("RED").GetComponent<Light>().intensity = 0;
    }

    void RedLight(int i){
        trafficLights[i].transform.Find("RED").GetComponent<Light>().intensity = 2;
        trafficLights[i].transform.Find("GREEN").GetComponent<Light>().intensity = 0;
        trafficLights[i].transform.Find("YELLOW").GetComponent<Light>().intensity = 0;
    }

    void CompareCars() {
        foreach(Position p in d.cars) {
            if (existingCars.Contains(p.id)) {
                GameObject car = FindCar(p.id);
                carMovement = car.GetComponent<CarMovement>();
                carMovement.dest = new Vector3(p.x, 0.12f, p.y);
            } else {
                newCar = Instantiate(carPrefab, new Vector3(p.x, 0.12f, p.y), Quaternion.identity);
                carMovement = newCar.GetComponent<CarMovement>();
                carMovement.id = p.id;
                existingCars.Add(p.id);
                newCar.transform.parent = carGroup.transform;
            }
        }
    }
    

    void FindDeletions() {
        bool existe;
        foreach(Transform car in carGroup.transform) {
            existe = false;
            foreach(Position p in d.cars) {
                if (car.GetComponent<CarMovement>().id == p.id) {
                    existe = true;
                    break;
                }
            }
            if(existe == false){
                car.gameObject.SetActive(false);
            }
        }
    }
    
    GameObject FindCar(int id) {
        foreach(Transform car in carGroup.transform) {
            if (car.GetComponent<CarMovement>().id == id) {
                return car.gameObject;
            }
        }

        return new GameObject();
    }

    IEnumerator Wait() {
        while(true){
            yield return new WaitForSeconds(0.3f);
            StartCoroutine(GetPositions());
        }
    }
 
    IEnumerator GetPositions() {
        // get data
        UnityWebRequest www = UnityWebRequest.Get("http://localhost:8000/");
        yield return www.SendWebRequest();
 
        if (www.result != UnityWebRequest.Result.Success) {
            Debug.Log(www.error);
        }
        else {
            // Show results as text
            //Debug.Log(www.downloadHandler.text);
        }

        d = JsonUtility.FromJson<Data>(www.downloadHandler.text);
        //print(d);

        UpdateTrafficLights();
        CompareCars();
        FindDeletions();
    }
}
