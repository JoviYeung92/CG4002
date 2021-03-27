#include <iostream>
#include <vector>
#include <fstream>
#include <string>
#include <sstream>
#include <math.h>
#include <utility>

using namespace std;

class DataPoint
{
public:
    int  roll, pitch, yaw, x, y, z;
    int time;
};

long euclidianDistance(vector<DataPoint> training, vector<DataPoint> test)
{
    int dist = 0;
    int len = training.size() > test.size() ? test.size() : training.size();
    for (int i = 0; i < len; i++)
    {

        dist += sqrt(pow(((int)training[i].x - (int)test[i].x), 2) + pow(((int)training[i].y - (int)test[i].y), 2) + pow(((int)training[i].z - (int)test[i].z), 2));
        //cout << sqrt(pow(((int)training[i].x - (int)test[i].x), 2) + pow(((int)training[i].y - (int)test[i].y), 2) + pow(((int)training[i].z - (int)test[i].z), 2)) << '\n';
    }
    //cout << dist << '\n';
    return dist;
}

vector<DataPoint> scanFile(string filepath)
{
    vector<DataPoint> dataPoints;
    ifstream dataFile;
    string currTestPath = filepath;
    string line;
    //cout << currTestPath << '\n' ;
    dataFile.open(currTestPath);
    while (getline(dataFile, line))
    {
        DataPoint dp;
        float x, y, z, roll, pitch, yaw;
        int time;
        istringstream iss(line);
        iss >>  roll >> yaw >> pitch >> x >> y >> z >>time;
        //cout << x << ' ' << y << ' '<< z << ' ' << roll << ' ' << yaw << ' ' << pitch << ' ' << time <<'\n';
        dp.x = (int)(abs(x) * 100);
        dp.y = (int)(abs(y) * 100);
        dp.z = (int)(abs(z) * 100);
        dp.roll = abs(roll);
        dp.pitch = abs(pitch);
        dp.yaw = abs(yaw);
        dp.time = abs(time);
        dataPoints.push_back(dp);
    }
    return dataPoints;
}

string predict(vector<vector<DataPoint>> train_zig_zag,
               vector<vector<DataPoint>> train_rocket,
               vector<vector<DataPoint>> train_hair,
               string testPath)
{
    vector<pair<long, int>> nearest;
    for (int i = 0; i < 3; i++)
    {
        nearest.push_back(make_pair(LONG_MAX, -1));
    }
    vector<DataPoint> test;
    test = scanFile(testPath);

    for (int i = 0; i < train_zig_zag.size(); i++)
    {
        vector<DataPoint> dpv = train_zig_zag[i];
        long d = euclidianDistance(dpv, test);
        for (int j = 0; j < 3; j++)
        {
            if (d < nearest[j].first)
            {
                nearest[j] = make_pair(d, 0);
                break;
            }
        }
    }

    for (int i = 0; i < train_rocket.size(); i++)
    {
        vector<DataPoint> dpv = train_rocket[i];
        long d = euclidianDistance(dpv, test);
        for (int j = 0; j < 3; j++)
        {
            if (d < nearest[j].first)
            {
                nearest[j] = make_pair(d, 1);
                break;
            }
        }
    }

    for (int i = 0; i < train_hair.size(); i++)
    {
        vector<DataPoint> dpv = train_hair[i];
        long d = euclidianDistance(dpv, test);
        for (int j = 0; j < 3; j++)
        {
            if (d < nearest[j].first)
            {
                nearest[j] = make_pair(d, 2);
                break;
            }
        }
    }

    vector<int> cnt(3, 0);
    for (int j = 0; j < 3; j++)
    {
        //cout << nearest[j].first << ' ' << nearest[j].second << '\n';
        cnt[nearest[j].second]++;
    }

    if (cnt[0] == cnt[1] && cnt[1] == cnt[2])
    {
        cout << "Draw";
    }
    else
    {
        int prev_largest = 0;
        int index_largest = 0;
        for (int j = 0; j < 3; j++)
        {
            if (cnt[j] > prev_largest)
            {
                prev_largest = cnt[j];
                index_largest = j;
            }
        }
        switch (index_largest)
        {
        case 0:
            return "ZigZag";
        case 1:
            return "Rocket";
        case 2:
            return "Hair";
        default:
            break;
        }
    }
    return 0;
}

int main()
{
    vector<vector<DataPoint>> train_zig_zag;
    vector<vector<DataPoint>> train_rocket;
    vector<vector<DataPoint>> train_hair;
    string zztrainPath = "../Datasets/Zig Zag - roll, pitch, yaw/Attempt ";
    for (int i = 1; i <= 7; i++)
    {
        vector<DataPoint> vdp = scanFile(zztrainPath + to_string(i) + ".TXT");
        train_zig_zag.push_back(vdp);
    }

    string rtrainPath = "../Datasets/Rocket - roll, pitch, yaw/Attempt ";
    for (int i = 1; i <= 7; i++)
    {
        vector<DataPoint> vdp = scanFile(rtrainPath + to_string(i) + ".TXT");
        train_rocket.push_back(vdp);
    }

    string htrainPath = "../Datasets/Hair - roll, pitch, yaw/Attempt ";
    for (int i = 1; i <= 7; i++)
    {
        vector<DataPoint> vdp = scanFile(htrainPath + to_string(i) + ".TXT");
        train_hair.push_back(vdp);
    }

    string testPath = "../Datasets/Zig Zag - roll, pitch, yaw/Attempt 8.TXT";
    cout << "Test file label: ZigZag" << "\n";
    cout << "Predicted: " << predict(train_zig_zag, train_rocket, train_hair, testPath) << '\n';

    testPath = "../Datasets/Rocket - roll, pitch, yaw/Attempt 8.TXT";
    cout << "Test file label: Rocket" << "\n";
    cout << "Predicted: " << predict(train_zig_zag, train_rocket, train_hair, testPath) << '\n';

    testPath = "../Datasets/Hair - roll, pitch, yaww/Attempt 8.TXT";
    cout << "Test file label: Hair" << "\n";
    cout << "Predicted: " << predict(train_zig_zag, train_rocket, train_hair, testPath) << '\n';
}
