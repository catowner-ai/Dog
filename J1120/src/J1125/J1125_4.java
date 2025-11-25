package J1125;

public class J1125_4 {

	public static void main(String[] args) {
		// TODO Auto-generated method stub
	
		factorial(5);
		factorial(8);

	}
		static void factorial(int x) {
		int i = x, j = 1;
		while(i > 0)
		    j *= i--;
		System.out.println(x + "! = " + j);
		}
	}


