
#pragma once
#include "math.h"

template<class T>
class RangeClip {
public:
  T min, max;
public:
  RangeClip(T aMin, T aMax)
  {
    min = aMin; max = aMax;
  }

  T Clip(T aVal)
  {
    if (aVal > max)
      return max;
    if (aVal < min)
      return min;
    return aVal;
  }
};


inline float ClipHL(float aVal, float aMax)
{
  if (aVal > aMax)
    return aMax;
  if (aVal < -aMax)
    return -aMax;
  return aVal;
}


class PIDParam {
public:
  PIDParam(float aKP, float aKD, float aKI, float aKS, const char* aName)
  {
    KP = aKP; KD = aKD; KI = aKI; on = 0; _name = aName;
    KS = aKS; rate = 0;
  }

  PIDParam()
  {
  }

  PIDParam(PIDParam& aPid)
  {
    Copy(aPid); on = 0;
  }

  void Copy(PIDParam& aPid)
  {
    KP = aPid.KP; KD = aPid.KD; KI = aPid.KI; _name = aPid._name;
    KS = aPid.KS; rate = aPid.rate; on = aPid.on;
  }

  void ReadCOM(SvProtocol3* aP)
  {
    aP->rdF(KP).rdF(KD).rdF(KI).rdF(KS).rdF(rate);
  }

  void WriteCOM(SvProtocol3* aP)
  {
    aP->WrStr(_name);
    aP->WrF(KP).WrF(KD).WrF(KI).WrF(KS).WrF(rate);
  }

  void Print(SvProtocol3* aP)
  {
    aP->SvPrintf("%s %1.1f %1.1f %1.1f %1.1f", _name, KP, KD, KI, KS);
  }
public:
  int16_t on;
  float KP, KD, KI, KS, rate;
  const char* _name;
};


inline void setGetControlParams(int cmd, SvProtocol3* aP, PIDParam* p1)
{
  if (cmd == 200) {
    int num = aP->ReadI16();
    p1->ReadCOM(aP);
    aP->SvMessage("Set PID");
  }
  if (cmd == 201) {
    int num = aP->ReadI16();
    aP->LockOStream();
    aP->WrB(200);
    p1->WriteCOM(aP);
    aP->Flush();
    aP->UnlockOStream();
    aP->SvMessage("Get PID");
  }
}



