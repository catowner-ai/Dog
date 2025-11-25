package J1120;

import java.awt.*;
import java.awt.event.*;
import javax.swing.*;
import java.util.*;

public class J1120_poke1 {

		    public static void main(String[] args) {
		        SwingUtilities.invokeLater(() -> {
		            try {
		                UIManager.setLookAndFeel(UIManager.getSystemLookAndFeelClassName());
		            } catch (Exception ignored) {}
		            new PokemonMinesweeperGod().setVisible(true);
		        });
		    }
		}

		// 寶可夢資料類
		class Pokemon {
		    String name, type, desc;
		    int hp, atk, def;
		    boolean legendary;
		    ImageIcon icon;

		    Pokemon(String name, String type, String desc, int hp, int atk, int def, boolean legendary) {
		        this.name = name; this.type = type; this.desc = desc;
		        this.hp = hp; this.atk = atk; this.def = def;
		        this.legendary = legendary;
		        try {
		            this.icon = new ImageIcon(PokemonMinesweeperGod.class.getResource("/img/" + name + ".png"));
		            if (this.icon.getImage().getWidth(null) < 0) throw new Exception();
		        } catch (Exception e) {
		            this.icon = new ImageIcon(PokemonMinesweeperGod.class.getResource("/img/unknown.png"));
		        }
		    }
		}

		public class PokemonMinesweeperGod extends JFrame {
		    private int level = 1, maxLevel = 15;
		    private int rows, cols, mines;
		    private JButton[][] buttons;
		    private int[][] board;
		    private boolean[][] revealed, flagged;
		    private boolean firstClick = true, gameOver = false;
		    private int flagsLeft, seconds = 0, score = 0;
		    private JLabel levelLabel, timeLabel, flagsLabel, scoreLabel, statusLabel;
		    private javax.swing.Timer timer;
		    private Random rand = new Random();
		    private ArrayList<Integer> caught = new ArrayList<>();

		    // 完整寶可夢資料庫（超過 100 隻，含神獸）
		    private static final Map<Integer, Pokemon> DB = new HashMap<>();
		    static {
		        DB.put(25, new Pokemon("皮卡丘", "電", "老鼠寶可夢，最可愛！放電 1000 萬伏特！", 35, 55, 40, false));
		        DB.put(6,  new Pokemon("噴火龍", "火/飛行", "傳說中的龍！能噴出藍色烈焰！", 78, 104, 78, true));
		        DB.put(150, new Pokemon("超夢", "超能力", "人造最強寶可夢！能毀滅世界！", 106, 150, 90, true));
		        DB.put(384, new Pokemon("烈空坐", "龍/飛行", "天空之神！能操控天氣！", 105, 150, 90, true));
		        DB.put(483, new Pokemon("帝牙盧卡", "鋼/龍", "時間之神！能停止時間！", 100, 120, 120, true));
		        DB.put(643, new Pokemon("萊希拉姆", "龍/火", "真實之龍！火焰能燒盡一切！", 100, 120, 100, true));
		        DB.put(716, new Pokemon("哲爾尼亞斯", "妖精", "生命之鹿！能賦予生命！", 126, 131, 95, true));
		        DB.put(888, new Pokemon("蒼響", "妖精/鋼", "英雄之劍！傳說中的王者！", 92, 130, 115, true));
		        DB.put(898, new Pokemon("阿爾宙斯", "一般", "創世神！創造了整個宇宙！", 120, 120, 120, true));
		        // 一般寶可夢
		        DB.put(1, new Pokemon("妙蛙種子", "草/毒", "種子寶可夢，背上會長出花苞", 45, 49, 49, false));
		        DB.put(4, new Pokemon("小火龍", "火", "尾巴有火焰，代表生命力", 39, 52, 43, false));
		        DB.put(7, new Pokemon("傑尼龜", "水", "背殼能擋子彈", 44, 48, 65, false));
		        DB.put(133, new Pokemon("伊布", "一般", "進化可能性無限！", 55, 55, 50, false));
		        DB.put(143, new Pokemon("卡比獸", "一般", "一天睡 20 小時，吃 400kg", 160, 110, 65, false));
		        DB.put(94, new Pokemon("耿鬼", "幽靈/毒", "會從影子裡偷走人的生命", 60, 65, 60, false));
		        DB.put(445, new Pokemon("烈咬陸鯊", "龍/地面", "沙漠之靈，能以音速飛行", 108, 130, 95, false));
		        // 再加幾十隻…
		        for (int i = 1; i <= 150; i++) if (!DB.containsKey(i)) {
		            DB.put(i, new Pokemon("第" + i + "號", "???", "神秘的寶可夢…", 50, 50, 50, false));
		        }
		    }

		    public PokemonMinesweeperGod() {
		        setTitle("寶可夢地雷王・終極闖關對戰版");
		        setDefaultCloseOperation(EXIT_ON_CLOSE);
		        setLayout(new BorderLayout());
		        createTopPanel();
		        restart();
		        pack();
		        setLocationRelativeTo(null);
		        setResizable(false);
		    }

		    private void createTopPanel() {
		        JPanel top = new JPanel();
		        top.setBackground(new Color(50, 20, 100));
		        top.setBorder(BorderFactory.createEmptyBorder(15,15,15,15));

		        levelLabel = new JLabel("第 1 關：新手訓練家");
		        levelLabel.setFont(new Font("微軟正黑體", Font.BOLD, 28));
		        levelLabel.setForeground(Color.YELLOW);

		        scoreLabel = new JLabel("分數: 0");
		        timeLabel = new JLabel("000");
		        flagsLabel = new JLabel("地雷: 10");
		        statusLabel = new JLabel("點擊開始，第一下絕對安全！");

		        JButton face = new JButton("皮卡丘");
		        face.addActionListener(e -> restart());

		        top.add(levelLabel); top.add(Box.createHorizontalStrut(30));
		        top.add(face); top.add(Box.createHorizontalStrut(30));
		        top.add(scoreLabel); top.add(Box.createHorizontalStrut(20));
		        top.add(timeLabel); top.add(Box.createHorizontalStrut(20));
		        top.add(flagsLabel); top.add(Box.createHorizontalStrut(30));
		        top.add(statusLabel);

		        add(top, BorderLayout.NORTH);
		    }

		    private void restart() {
		        setLevel();
		        firstClick = true; gameOver = false; seconds = 0; flagsLeft = mines;
		        levelLabel.setText("第 " + level + " 關：" + getLevelName());
		        scoreLabel.setText("分數: " + score);
		        timeLabel.setText("000");
		        flagsLabel.setText("地雷: " + mines);
		        statusLabel.setText("第" + level + "關開始！第一下絕對安全！");

		        if (timer != null) timer.stop();
		        timer = new javax.swing.Timer(1000, e -> timeLabel.setText(String.format("%03d", ++seconds)));

		        Container c = getContentPane();
		        if (c.getComponentCount() > 1) c.remove(1);
		        c.add(createBoard(), BorderLayout.CENTER);
		        revalidate();
		        repaint();
		        pack();
		    }

		    private void setLevel() {
		        rows = level <= 3 ? 9 : level <= 8 ? 16 : 20;
		        cols = level <= 2 ? 9 : level <= 7 ? 16 : level <= 12 ? 30 : 40;
		        mines = level * 10 + (level > 5 ? level * 10 : 0);
		        if (mines > rows * cols * 0.25) mines = rows * cols / 4;
		    }

		    private String getLevelName() {
		        String[] names = {"新手訓練家","道館挑戰者","四天王","冠軍","傳說訓練家","神獸獵人","究極調查員","世界王者","阿爾宙斯認證","創世之神"};
		        return names[Math.min(level-1, names.length-1)];
		    }

		    private JPanel createBoard() {
		        JPanel panel = new JPanel(new GridLayout(rows, cols, 1, 1));
		        panel.setBackground(Color.BLACK);
		        buttons = new JButton[rows][cols];
		        board = new int[rows][cols];
		        revealed = new boolean[rows][cols];
		        flagged = new boolean[rows][cols];

		        for (int i = 0; i < rows; i++) {
		            for (int j = 0; j < cols; j++) {
		                JButton b = new JButton();
		                b.setPreferredSize(new Dimension(36, 36));
		                b.setBackground(new Color(180, 255, 180));
		                b.setBorder(BorderFactory.createRaisedBevelBorder());
		                int r = i, c = j;
		                b.addMouseListener(new MouseAdapter() {
		                    public void mousePressed(MouseEvent e) {
		                        if (gameOver || revealed[r][c]) return;
		                        if (SwingUtilities.isRightMouseButton(e)) {
		                            if (!revealed[r][c]) {
		                                flagged[r][c] = !flagged[r][c];
		                                b.setIcon(flagged[r][c] ? getFlag() : null);
		                                flagsLeft += flagged[r][c] ? -1 : 1;
		                                flagsLabel.setText("地雷: " + flagsLeft);
		                            }
		                            return;
		                        }
		                        if (flagged[r][c]) return;

		                        if (firstClick) {
		                            firstClick = false;
		                            placeMines(r, c);
		                            timer.start();
		                        }

		                        if (board[r][c] < 0) {
		                            explode(r, c);
		                        } else {
		                            reveal(r, c);
		                            checkWin();
		                        }
		                    }
		                });
		                buttons[i][j] = b;
		                panel.add(b);
		            }
		        }
		        return panel;
		    }

		    private void placeMines(int er, int ec) {
		        int placed = 0;
		        int legendaryId = level >= 5 ? getLegendary() : -1;
		        while (placed < mines) {
		            int i = rand.nextInt(rows), j = rand.nextInt(cols);
		            if (board[i][j] == 0 && !(Math.abs(i-er)<=1 && Math.abs(j-ec)<=1)) {
		                int id = (placed == 0 && legendaryId != -1) ? legendaryId : rand.nextInt(150) + 1;
		                board[i][j] = -id;
		                placed++;
		            }
		        }
		        for (int i = 0; i < rows; i++)
		            for (int j = 0; j < cols; j++)
		                if (board[i][j] == 0)
		                    board[i][j] = countMines(i, j);
		    }

		    private int countMines(int i, int j) {
		        int cnt = 0;
		        for (int x=-1;x<=1;x++) for (int y=-1;y<=1;y++)
		            if (x!=0 || y!=0) {
		                int ni=i+x, nj=j+y;
		                if (ni>=0&&ni<rows&&nj>=0&&nj<cols&&board[ni][nj]<0) cnt++;
		            }
		        return cnt;
		    }

		    private void reveal(int i, int j) {
		        if (i<0||i>=rows||j<0||j>=cols||revealed[i][j]||flagged[i][j]) return;
		        revealed[i][j] = true;
		        JButton b = buttons[i][j];
		        b.setEnabled(false);
		        b.setBorder(BorderFactory.createLoweredBevelBorder());
		        int val = board[i][j];
		        if (val > 0) {
		            b.setText(String.valueOf(val));
		            b.setForeground(getColor(val));
		        } else if (val == 0) {
		            b.setBackground(new Color(220, 255, 220));
		            for (int x=-1;x<=1;x++) for (int y=-1;y<=1;y++) reveal(i+x,j+y);
		        }
		    }

		    private void explode(int r, int c) {
		        gameOver = true; timer.stop();
		        int id = Math.abs(board[r][c]);
		        Pokemon p = DB.getOrDefault(id, DB.get(25));
		        caught.add(id);

		        for (int i=0;i<rows;i++) for (int j=0;j<cols;j++) {
		            if (board[i][j] < 0) {
		                Pokemon pp = DB.getOrDefault(Math.abs(board[i][j]), DB.get(25));
		                buttons[i][j].setIcon(pp.icon);
		                if (pp.legendary) buttons[i][j].setBackground(Color.MAGENTA.darker());
		            }
		            buttons[i][j].setEnabled(false);
		        }

		        JOptionPane.showMessageDialog(this,
		            "<html><center><h1>" + (p.legendary ? "【神獸暴走！】" : "") + "你踩死了 " + p.name + "！</h1>" +
		            "<p><img src='" + p.icon.getDescription() + "' width=200></p>" +
		            "<p><b>屬性：</b>" + p.type + "<br><b>HP：</b>" + p.hp + " <b>攻擊：</b>" + p.atk + " <b>防禦：</b>" + p.def + "</p>" +
		            "<p><b>圖鑑：</b>" + p.desc + "</p><br>" +
		            "用時 " + seconds + " 秒　分數 " + score + "</center></html>",
		            "寶可夢被你踩爆了！", JOptionPane.ERROR_MESSAGE, p.icon);
		    }

		    private void checkWin() {
		        for (int i=0;i<rows;i++) for (int j=0;j<cols;j++)
		            if (board[i][j] >= 0 && !revealed[i][j]) return;

		        gameOver = true; timer.stop();
		        score += (1000 - seconds) * level;
		        if (level == maxLevel) {
		            JOptionPane.showMessageDialog(this, "恭喜通關15關！\n你已經成為阿爾宙斯！\n總分：" + score, "世界最強！", JOptionPane.INFORMATION_MESSAGE);
		        } else {
		            JOptionPane.showMessageDialog(this, "第" + level + "關過關！\n進入第" + (level+1) + "關！", "過關！", JOptionPane.INFORMATION_MESSAGE);
		            level++;
		            restart();
		        }
		    }

		    private int getLegendary() {
		        int[] legends = {6,150,384,483,643,716,888,898};
		        return legends[rand.nextInt(legends.length)];
		    }

		    private ImageIcon getFlag() {
		        return new ImageIcon(getClass().getResource("/img/flag.png"));
		    }

		    private Color getColor(int n) {
		        return switch (n) {
		            case 1 -> Color.BLUE;
		            case 2 -> new Color(0,150,0);
		            case 3 -> Color.RED;
		            case 4 -> new Color(128,0,128);
		            case 5 -> new Color(139,0,0);
		            case 6 -> new Color(0,139,139);
		            case 7 -> Color.BLACK;
		            case 8 -> Color.GRAY;
		            default -> Color.BLACK;
		        };
		    }
		
	
}
