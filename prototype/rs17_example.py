import tims_converter as tc
import alphatims.bruker


if __name__ == '__main__':
    meoh = alphatims.bruker.TimsTOF('F:\\itzel_tims\\meoh_tims_ms2_37_1_1106.d')
    meleagrin = alphatims.bruker.TimsTOF('F:\\itzel_tims\\meleagrine_tims_ms2_39_1_1102.d')
    roqc = alphatims.bruker.TimsTOF('F:\\itzel_tims\\roq_c_tims_ms2_40_1_1103.d')
    rs17 = alphatims.bruker.TimsTOF('F:\\itzel_tims\\rs17_xad247_tims_ms2_41_1_1105.d')

    meoh[:, :, :, :, :].to_csv('meoh_smcomm.csv')
    meleagrin[:, :, :, :, :].to_csv('meleagrin_smcomm.csv')
    roqc[:, :, :, :, :].to_csv('roqc_smcomm.csv')
    rs17[:, :, :, :, :].to_csv('rs17_smcomm.csv')