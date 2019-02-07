using System;
using System.IO;
using System.Net;

namespace ConsoleApp2
{
    class Program
    {
        static void Main(string[] args)
        {
            test();
        }

        static void test()
        {
            var ip = "192.168.1.24";
            var fromLat = 34.86415;
            var fromLon = 32.28841;
            var toLat = 34.86209;
            var toLon = 32.29324;
            var uri = String.Format("http://{0}:5000/api/v1/route?from={1},{2}&to={3},{4}", ip, fromLat, fromLon, toLat, toLon);

            var request = (HttpWebRequest)WebRequest.Create(uri);
            var response = (HttpWebResponse)request.GetResponse();
            var responseString = new StreamReader(response.GetResponseStream()).ReadToEnd();
            Console.Write(responseString);
        }
    }
}

