package J1125;

public class J1125_1 {

	public static void main(String[] args) {
		// TODO Auto-generated method stub
		int[][] n = new int[3][];
		n[0] = new int[] {1};
		n[1] = new int[] {2, 3};
		n[2] = new int[] {4, 5, 6};
		for (int i = 0; i < n.length ; i++){
		    for (int j = 0 ; j<n[i].length ; j++)
		        System.out.print(" " + n[i][j]);
		    System.out.println();
		}
	}

}
