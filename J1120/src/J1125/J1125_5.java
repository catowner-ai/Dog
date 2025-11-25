package J1125;

public class J1125_5 {

	public static void main(String[] args) {
		// TODO Auto-generated method stub

		int a = 10, b = 15;
		System.out.println(" 傳值呼叫前\ta=" + a + "\tb=" + b );
		byVal(a, b);
		System.out.println(" 傳值呼叫後\ta=" + a + "\tb=" + b );

	}
		static void byVal(int x, int y) {
		    int t;
		    t = x;
		    x = y;
		    y = t;
		System.out.println(" 傳值呼叫中\tx=" + x + "\ty=" + y );
		}
	}


