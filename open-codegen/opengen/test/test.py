import unittest
import casadi.casadi as cs
import opengen as og
import subprocess


class RustBuildTestCase(unittest.TestCase):

    TEST_DIR = ".python_test_build"

    @classmethod
    def solverConfig(cls):
        solver_config = og.config.SolverConfiguration() \
            .with_lfbgs_memory(15) \
            .with_tolerance(1e-4) \
            .with_initial_tolerance(1e-4) \
            .with_delta_tolerance(1e-4) \
            .with_initial_penalty(15.0) \
            .with_penalty_weight_update_factor(10.0) \
            .with_max_inner_iterations(155) \
            .with_max_duration_micros(1e8) \
            .with_max_outer_iterations(50) \
            .with_sufficient_decrease_coefficient(0.05) \
            .with_cbfgs_parameters(1.5, 1e-10, 1e-12)
        return solver_config

    @classmethod
    def setUpOnlyF1(cls):
        u = cs.MX.sym("u", 5)  # decision variable (nu = 5)
        p = cs.MX.sym("p", 2)  # parameter (np = 2)
        f1 = cs.vertcat(1.5 * u[0] - u[1], u[2] - u[3])
        set_c = og.constraints.BallInf([0.0, 0.1], 0.001)
        set_y = og.constraints.BallInf(None, 1e12)
        phi = og.functions.rosenbrock(u, p)  # cost function
        bounds = og.constraints.Ball2(None, 1.5)  # ball centered at origin
        tcp_config = og.config.TcpServerConfiguration(bind_port=3301)
        meta = og.config.OptimizerMeta() \
            .with_optimizer_name("only_f1")
        problem = og.builder.Problem(u, p, phi) \
            .with_aug_lagrangian_constraints(f1, set_c, set_y) \
            .with_constraints(bounds)
        build_config = og.config.BuildConfiguration() \
            .with_build_directory(RustBuildTestCase.TEST_DIR) \
            .with_build_mode("debug") \
            .with_tcp_interface_config(tcp_interface_config=tcp_config) \
            .with_build_c_bindings()
        og.builder.OpEnOptimizerBuilder(problem,
                                        metadata=meta,
                                        build_configuration=build_config,
                                        solver_configuration=cls.solverConfig()) \
            .build()

    @classmethod
    def setUpOnlyF2(cls):
        u = cs.MX.sym("u", 5)  # decision variable (nu = 5)
        p = cs.MX.sym("p", 2)  # parameter (np = 2)
        f2 = cs.vertcat(0.2 + 1.5 * u[0] - u[1], u[2] - u[3] - 0.1)
        phi = og.functions.rosenbrock(u, p)
        bounds = og.constraints.Ball2(None, 1.5)
        tcp_config = og.config.TcpServerConfiguration(bind_port=3302)
        meta = og.config.OptimizerMeta() \
            .with_optimizer_name("only_f2")
        problem = og.builder.Problem(u, p, phi) \
            .with_penalty_constraints(f2) \
            .with_constraints(bounds)
        build_config = og.config.BuildConfiguration() \
            .with_build_directory(RustBuildTestCase.TEST_DIR) \
            .with_build_mode("debug") \
            .with_tcp_interface_config(tcp_interface_config=tcp_config) \
            .with_build_c_bindings()
        og.builder.OpEnOptimizerBuilder(problem,
                                        metadata=meta,
                                        build_configuration=build_config,
                                        solver_configuration=cls.solverConfig()) \
            .build()

    @classmethod
    def setUpPlain(cls):
        u = cs.MX.sym("u", 5)  # decision variable (nu = 5)
        p = cs.MX.sym("p", 2)  # parameter (np = 2)
        phi = og.functions.rosenbrock(u, p)
        bounds = og.constraints.Ball2(None, 1.5)
        tcp_config = og.config.TcpServerConfiguration(bind_port=3302)
        meta = og.config.OptimizerMeta() \
            .with_optimizer_name("plain")
        problem = og.builder.Problem(u, p, phi) \
            .with_constraints(bounds)
        build_config = og.config.BuildConfiguration() \
            .with_build_directory(RustBuildTestCase.TEST_DIR) \
            .with_build_mode("debug") \
            .with_tcp_interface_config(tcp_interface_config=tcp_config) \
            .with_build_c_bindings()
        og.builder.OpEnOptimizerBuilder(problem,
                                        metadata=meta,
                                        build_configuration=build_config,
                                        solver_configuration=cls.solverConfig()) \
            .build()

    @classmethod
    def setUpClass(cls):
        cls.setUpOnlyF1()
        cls.setUpOnlyF2()
        cls.setUpPlain()

    def test_rectangle_empty(self):
        xmin = [-1, 2]
        xmax = [-2, 4]
        with self.assertRaises(Exception) as __context:
            og.constraints.Rectangle(xmin, xmax)

    def test_rectangle_incompatible_dimensions(self):
        xmin = [-1, -1, 1]
        xmax = [1, 1]
        with self.assertRaises(Exception) as __context:
            og.constraints.Rectangle(xmin, xmax)

    def test_rectangle_both_none(self):
        with self.assertRaises(Exception) as __context:
            og.constraints.Rectangle(None, None)

    def test_ball_negative_radius(self):
        with self.assertRaises(Exception) as __context:
            og.constraints.Ball2(None, -1)

    def test_solver_config_wrong_max_duration(self):
        with self.assertRaises(Exception) as __context:
            og.config.SolverConfiguration().with_max_duration_micros(0)

    def test_solver_config_wrong_update_factor(self):
        with self.assertRaises(Exception) as __context:
            og.config.SolverConfiguration().with_penalty_weight_update_factor(0.5)

    def test_solver_config_wrong_outer_iterations(self):
        with self.assertRaises(Exception) as __context:
            og.config.SolverConfiguration().with_max_outer_iterations(0)

    def test_solver_config_wrong_inner_iterations(self):
        with self.assertRaises(Exception) as __context:
            og.config.SolverConfiguration().with_max_inner_iterations(0)

    def test_solver_config_wrong_constraints_tolerance(self):
        with self.assertRaises(Exception) as __context:
            og.config.SolverConfiguration().with_delta_tolerance(0)

    def test_solver_config_wrong_inner_tolerance(self):
        with self.assertRaises(Exception) as __context:
            og.config.SolverConfiguration().with_tolerance(0)

    def test_solver_config_wrong_lbfgs_memory(self):
        with self.assertRaises(Exception) as __context:
            og.config.SolverConfiguration().with_lfbgs_memory(1)

    def test_solver_config_wrong_max_inner_iterations(self):
        with self.assertRaises(Exception) as __context:
            og.config.SolverConfiguration().with_max_inner_iterations()

    def test_rust_build_only_f1(self):
        mng = og.tcp.OptimizerTcpManager(RustBuildTestCase.TEST_DIR + '/only_f1')
        mng.start()
        pong = mng.ping()  # check if the server is alive
        self.assertEqual(1, pong["Pong"])

        # Regular call
        response = mng.call(p=[2.0, 10.0])
        self.assertEqual("Converged", response["exit_status"])

        # Call with initial params, initial y and initial penalty param
        response = mng.call(p=[2.0, 10.0],
                            initial_guess=response["solution"],
                            initial_y=response["lagrange_multipliers"],
                            initial_penalty=response["penalty"])
        self.assertEqual(2, response["num_outer_iterations"])

        response = mng.call(p=[2.0, 10.0, 50.0])
        self.assertEqual("Error", response["type"])
        self.assertEqual(3003, response["code"])

        response = mng.call(p=[2.0, 10.0], initial_guess=[0.1, 0.2])
        self.assertEqual("Error", response["type"])
        self.assertEqual(1600, response["code"])

        response = mng.call(p=[2.0, 10.0], initial_y=[0.1])
        self.assertEqual("Error", response["type"])
        self.assertEqual(1700, response["code"])

        mng.kill()

    def test_rust_build_only_f2(self):
        mng = og.tcp.OptimizerTcpManager(RustBuildTestCase.TEST_DIR + '/only_f2')
        mng.start()
        pong = mng.ping()  # check if the server is alive
        self.assertEqual(1, pong["Pong"])

        # Regular call
        response = mng.call(p=[2.0, 10.0])
        self.assertEqual("Converged", response["exit_status"])

        # Call with initial params, initial y and initial penalty param
        response = mng.call(p=[2.0, 10.0],
                            initial_guess=response["solution"],
                            initial_penalty=response["penalty"])
        self.assertEqual(1, response["num_outer_iterations"])

        response = mng.call(p=[2.0, 10.0, 50.0])
        self.assertEqual("Error", response["type"])
        self.assertEqual(3003, response["code"])

        response = mng.call(p=[2.0, 10.0], initial_guess=[0.1, 0.2])
        self.assertEqual("Error", response["type"])
        self.assertEqual(1600, response["code"])

        response = mng.call(p=[2.0, 10.0], initial_y=[0.1])
        self.assertEqual("Error", response["type"])
        self.assertEqual(1700, response["code"])

        mng.kill()

    def test_rust_build_only_f2(self):
        mng = og.tcp.OptimizerTcpManager(RustBuildTestCase.TEST_DIR + '/plain')
        mng.start()
        pong = mng.ping()  # check if the server is alive
        self.assertEqual(1, pong["Pong"])

        # Regular call
        response = mng.call(p=[2.0, 10.0])
        self.assertEqual("Converged", response["exit_status"])

    # def test_link_2_c_libs(self):
    #     u = cs.SX.sym("u", 5)
    #     p = cs.SX.sym("p", 2)
    #     phi = og.functions.rosenbrock(u, p)
    #     c = cs.vertcat(1.5*u[0] - u[1], u[2] - u[3])
    #     xmin = [-2.0, -2.0, -2.0, -2.0, -2.0]
    #     xmax = [ 2.0,  2.0,  2.0,  2.0,  2.0]
    #     bounds = og.constraints.Rectangle(xmin, xmax)
    #     problem = og.builder.Problem(u, p, phi) \
    #         .with_penalty_constraints(c)        \
    #         .with_constraints(bounds)
    #     meta1 = og.config.OptimizerMeta()               \
    #         .with_version("0.0.0")                      \
    #         .with_authors(["P. Sopasakis", "E. Fresk"]) \
    #         .with_licence("CC4.0-By")                   \
    #         .with_optimizer_name("the_optimizer1")
    #     meta2 = og.config.OptimizerMeta()               \
    #         .with_version("0.0.0")                      \
    #         .with_authors(["P. Sopasakis", "E. Fresk"]) \
    #         .with_licence("CC4.0-By")                   \
    #         .with_optimizer_name("the_optimizer2")
    #     build_config = og.config.BuildConfiguration()          \
    #         .with_rebuild(False)                               \
    #         .with_build_mode("debug")                          \
    #         .with_build_directory(RustBuildTestCase.TEST_DIR)  \
    #         .with_build_c_bindings()
    #     solver_config = og.config.SolverConfiguration()   \
    #         .with_lfbgs_memory(15)                        \
    #         .with_tolerance(1e-5)                         \
    #         .with_max_inner_iterations(155)               \
    #         .with_delta_tolerance(1e-4)             \
    #         .with_max_outer_iterations(15)                \
    #         .with_penalty_weight_update_factor(8.0)       \
    #         .with_initial_penalty_weights([20.0, 5.0])
    #
    #     builder1 = og.builder.OpEnOptimizerBuilder(problem,
    #                                               metadata=meta1,
    #                                               build_configuration=build_config,
    #                                               solver_configuration=solver_config) \
    #         .with_generate_not_build_flag(False).with_verbosity_level(0)
    #     builder1.build()
    #
    #     builder2 = og.builder.OpEnOptimizerBuilder(problem,
    #                                               metadata=meta2,
    #                                               build_configuration=build_config,
    #                                               solver_configuration=solver_config) \
    #         .with_generate_not_build_flag(False).with_verbosity_level(0)
    #     builder2.build()
    #
    #     p = subprocess.Popen(["gcc",
    #         "test/test_2_solvers.c",
    #         "-I" + RustBuildTestCase.TEST_DIR + "/the_optimizer1",
    #         "-I" + RustBuildTestCase.TEST_DIR + "/the_optimizer2",
    #         "-pthread",
    #         RustBuildTestCase.TEST_DIR + "/the_optimizer1/target/debug/libthe_optimizer1.a",
    #         RustBuildTestCase.TEST_DIR + "/the_optimizer2/target/debug/libthe_optimizer2.a",
    #         "-lm",
    #         "-ldl",
    #         "-std=c99",
    #         "-o" + RustBuildTestCase.TEST_DIR + "/test_2_solvers"],
    #         #stdin=subprocess.PIPE,
    #         stdout=subprocess.PIPE,
    #         stderr=subprocess.PIPE)
    #
    #     output, err = p.communicate()
    #     rc = p.returncode
    #
    #     print("gcc output: ")
    #     print(output.decode("utf-8"))
    #     print("gcc err: ")
    #     print(err.decode("utf-8"))
    #     print("gcc rc: ")
    #     print(rc)
    #
    #     if rc != 0:
    #         exit(rc)
    #
    #     p = subprocess.Popen(["./" + RustBuildTestCase.TEST_DIR + "/test_2_solvers"],
    #         #stdin=subprocess.PIPE,
    #         stdout=subprocess.PIPE,
    #         stderr=subprocess.PIPE)
    #
    #     output, err = p.communicate()
    #     rc = p.returncode
    #
    #     print("test_2_solvers output: ")
    #     print(output.decode("utf-8"))
    #     print("test_2_solvers err: ")
    #     print(err.decode("utf-8"))
    #     print("test_2_solvers rc: ")
    #     print(rc)
    #
    #     if rc != 0:
    #         exit(rc)
    #

    
if __name__ == '__main__':
    unittest.main()
